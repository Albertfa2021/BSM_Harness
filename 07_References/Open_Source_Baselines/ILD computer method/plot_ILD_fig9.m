% plot_ILD_fig9.m
% Reproduce the ILD analysis of Fig. 9(a) from Madmoni et al. 2025
% using the local AuditoryToolbox ERB filter bank implementation.
%
% The script follows the same BSM reproduction setup as plot_ITD_fig8.m
% and evaluates:
%   1. Average ILD over 29 ERB bands in [50, 6000] Hz
%   2. Averaged ILD error relative to the reference HRIR
%
% Reference: Section 7.5, Equations (44)-(46) of:
% "Design and Analysis of Binaural Signal Matching with Arbitrary
%  Microphone Arrays and Listener Head Rotations"

clc; clear; close all;

%% ========================================================================
%  Configuration Parameters
% =========================================================================

% HRIR dataset
hrir_filename = 'HRIR_L2702.mat';

% BSM Parameters
Q = 240;              % Number of assumed sources (spiral points)
filter_length = 512;  % BSM filter length
SNR_dB = 20;          % Signal-to-Noise Ratio in dB
N_order = 30;         % Spherical harmonic order

% Sampling frequency
fs = 48000;  % 48 kHz

% ILD analysis parameters from the paper
num_erb_bands = 29;
erb_low_hz = 50;
erb_high_hz = 6000;

% Test directions: theta = 90 deg, phi from 0 deg to 359 deg
azimuth_test = (0:1:359)';
elevation_test = 90 * ones(size(azimuth_test));
num_test_angles = length(azimuth_test);

fprintf('=== ILD Analysis for Fig. 9(a) Reproduction ===\n');
fprintf('Test angles: %d directions on equatorial plane (theta = 90 deg)\n', num_test_angles);
fprintf('Azimuth range: 0 deg to 359 deg (step: 1 deg)\n');
fprintf('ERB bands: %d bands in [%.0f, %.0f] Hz\n', num_erb_bands, erb_low_hz, erb_high_hz);

%% ========================================================================
%  Define Microphone Array Configuration
% =========================================================================

fprintf('\n=== Microphone Array Configuration ===\n');

array_radius = 0.10;  % 10 cm radius
M = 6;                % Number of microphones

mic_indices = 1:M;
array_config.theta_mic = ones(M, 1) * (pi/2);  % All on equator
array_config.phi_mic = (pi/2 - pi * (mic_indices - 1) / (M - 1))';
array_config.radius = array_radius;

fprintf('Array: Semi-circular rigid sphere, M=%d, radius=%.3f m\n', M, array_radius);

%% ========================================================================
%  Compute or Load BSM Filters
% =========================================================================

fprintf('\n=== BSM Filter Computation ===\n');

if exist('BSM_results.mat', 'file')
    fprintf('Loading existing BSM results from BSM_results.mat...\n');
    load('BSM_results.mat', 'results');
    c_BSM_left = results.c_BSM_left;
    c_BSM_right = results.c_BSM_right;
    freq_bins = results.freq_bins;

    if results.parameters.filter_length ~= filter_length || ...
       results.parameters.Q ~= Q || results.parameters.SNR_dB ~= SNR_dB
        warning('Existing BSM parameters do not match. Recomputing...');
        compute_bsm = true;
    else
        compute_bsm = false;
        fprintf('BSM filters loaded successfully.\n');
    end
else
    compute_bsm = true;
end

if compute_bsm
    fprintf('Computing BSM filters...\n');
    tic;
    [c_BSM_left, c_BSM_right, freq_bins] = ...
        BSM_reproduction(hrir_filename, array_config, Q, filter_length, SNR_dB, N_order);
    fprintf('BSM computation time: %.2f seconds\n', toc);
end

n_freqs = length(freq_bins);

%% ========================================================================
%  Load HRIR Data and Setup
% =========================================================================

fprintf('\n=== Loading HRIR Data ===\n');

addpath('KU100 dataset');
addpath('SphArrayProc/matlab/math');
addpath('AuditoryToolbox');

hrir_path = fullfile('KU100 dataset', hrir_filename);
load(hrir_path);
[~, var_name, ~] = fileparts(hrir_filename);
hrir_obj = eval(var_name);

load('Beyerdynamic-DT990PRO.mat', 'hpcf');
hrir_obj = hrir_obj.setHeadPhones(hpcf);
hrir_obj = setDEG(hrir_obj);

fprintf('HRIR data loaded and compensated.\n');

%% ========================================================================
%  Design ERB Filter Bank with AuditoryToolbox
% =========================================================================

fprintf('\n=== Designing ERB Filter Bank ===\n');

center_freqs_hz = sort(ERBSpace(erb_low_hz, erb_high_hz, num_erb_bands), 'ascend');
erb_filter_coefs = MakeERBFilters(fs, center_freqs_hz);

fprintf('Created %d ERB filters using AuditoryToolbox.\n', num_erb_bands);
fprintf('Center frequency range: %.1f Hz to %.1f Hz\n', ...
    min(center_freqs_hz), max(center_freqs_hz));

%% ========================================================================
%  ILD Calculation for Each Test Direction
% =========================================================================

fprintf('\n=== Computing ILD for %d Directions ===\n', num_test_angles);

c = 343;  % m/s

ILD_reference_bands = zeros(num_erb_bands, num_test_angles);
ILD_BSM_bands = zeros(num_erb_bands, num_test_angles);

fprintf('Progress: ');
progress_step = max(1, round(num_test_angles / 20));

for angle_idx = 1:num_test_angles

    if mod(angle_idx, progress_step) == 0
        fprintf('.');
    end

    az_deg = azimuth_test(angle_idx);
    el_deg = elevation_test(angle_idx);

    phi_test = az_deg * pi/180;
    theta_test = el_deg * pi/180;

    %% Step 1: Get reference HRIR for this direction
    [irID, ~, ~] = closestIr(hrir_obj, az_deg, el_deg);
    hrir_stereo = getIR(hrir_obj, irID);

    if size(hrir_stereo, 1) > filter_length
        hrir_stereo = hrir_stereo(1:filter_length, :);
    else
        hrir_stereo = [hrir_stereo; zeros(filter_length - size(hrir_stereo, 1), 2)];
    end

    hrir_ref_left = hrir_stereo(:, 1);
    hrir_ref_right = hrir_stereo(:, 2);

    %% Step 2: Compute BSM reproduced binaural signals
    k_wave = 2*pi*freq_bins / c;
    V_test = zeros(M, n_freqs);

    for f_idx = 1:n_freqs
        kr = k_wave(f_idx) * array_config.radius;
        V_test(:, f_idx) = SteeringVector(N_order, theta_test, phi_test, ...
                                          array_config.theta_mic, array_config.phi_mic, kr);
    end

    P_BSM_left_freq = zeros(n_freqs, 1);
    P_BSM_right_freq = zeros(n_freqs, 1);

    for f_idx = 1:n_freqs
        P_BSM_left_freq(f_idx) = c_BSM_left(:, f_idx)' * V_test(:, f_idx);
        P_BSM_right_freq(f_idx) = c_BSM_right(:, f_idx)' * V_test(:, f_idx);
    end

    P_BSM_left_full = [P_BSM_left_freq; conj(P_BSM_left_freq(end-1:-1:2))];
    P_BSM_right_full = [P_BSM_right_freq; conj(P_BSM_right_freq(end-1:-1:2))];

    p_BSM_left = real(ifft(P_BSM_left_full));
    p_BSM_right = real(ifft(P_BSM_right_full));

    %% Step 3: ERB band analysis using AuditoryToolbox
    ref_left_erb = ERBFilterBank(hrir_ref_left(:).', erb_filter_coefs);
    ref_right_erb = ERBFilterBank(hrir_ref_right(:).', erb_filter_coefs);
    bsm_left_erb = ERBFilterBank(p_BSM_left(:).', erb_filter_coefs);
    bsm_right_erb = ERBFilterBank(p_BSM_right(:).', erb_filter_coefs);

    ref_left_power = sum(abs(ref_left_erb).^2, 2);
    ref_right_power = sum(abs(ref_right_erb).^2, 2);
    bsm_left_power = sum(abs(bsm_left_erb).^2, 2);
    bsm_right_power = sum(abs(bsm_right_erb).^2, 2);

    ILD_reference_bands(:, angle_idx) = 10 * log10((ref_left_power + eps) ./ (ref_right_power + eps));
    ILD_BSM_bands(:, angle_idx) = 10 * log10((bsm_left_power + eps) ./ (bsm_right_power + eps));
end

fprintf(' Done!\n');

%% ========================================================================
%  Average ILD and Averaged ILD Error
% =========================================================================

% Equation (45): average ILD across ERB bands
ILD_reference_avg = mean(ILD_reference_bands, 1).';
ILD_BSM_avg = mean(ILD_BSM_bands, 1).';

% Equation (46): averaged ILD error across ERB bands
ILD_error_avg = mean(abs(ILD_BSM_bands - ILD_reference_bands), 1).';

fprintf('\nILD Statistics:\n');
fprintf('Reference average ILD range: [%.2f, %.2f] dB\n', ...
    min(ILD_reference_avg), max(ILD_reference_avg));
fprintf('BSM average ILD range: [%.2f, %.2f] dB\n', ...
    min(ILD_BSM_avg), max(ILD_BSM_avg));
fprintf('Average ILD error mean: %.2f dB\n', mean(ILD_error_avg));
fprintf('Average ILD error max: %.2f dB\n', max(ILD_error_avg));

%% ========================================================================
%  Visualization: Reproduce Fig. 9(a)-style Curves
% =========================================================================

fprintf('\n=== Generating Fig. 9(a)-Style Visualization ===\n');

figure('Name', 'Figure 9(a): ILD Analysis (No Head Rotation)', ...
       'Position', [100 100 1200 800]);

subplot(2, 1, 1);
plot(azimuth_test, ILD_reference_avg, 'b-', 'LineWidth', 2, ...
    'DisplayName', 'Reference HRIR');
hold on;
plot(azimuth_test, ILD_BSM_avg, 'r--', 'LineWidth', 1.5, ...
    'DisplayName', 'BSM');
grid on;
xlabel('Azimuth Angle \phi (degrees)', 'FontSize', 12);
ylabel('Average ILD (dB)', 'FontSize', 12);
title('Estimated Average ILD vs Azimuth (\theta = 90 deg, No Head Rotation)', ...
    'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
xlim([0 359]);
set(gca, 'FontSize', 11);

subplot(2, 1, 2);
plot(azimuth_test, ILD_error_avg, 'k-', 'LineWidth', 1.5);
hold on;
yline(1.0, 'r--', 'LineWidth', 1.5, 'DisplayName', 'JND Threshold (1 dB)');
grid on;
xlabel('Azimuth Angle \phi (degrees)', 'FontSize', 12);
ylabel('Averaged ILD Error (dB)', 'FontSize', 12);
title('Averaged ILD Error (Absolute Difference from Reference)', ...
    'FontSize', 14, 'FontWeight', 'bold');
legend('ILD Error', 'JND Threshold (1 dB)', 'Location', 'best', 'FontSize', 11);
xlim([0 359]);
ylim([0 max([max(ILD_error_avg) * 1.1, 2])]);
set(gca, 'FontSize', 11);

sgtitle(sprintf(['ILD Analysis: M=%d mics, Q=%d sources, SNR=%d dB, ' ...
                 '%d ERB bands in [%d, %d] Hz'], ...
        M, Q, SNR_dB, num_erb_bands, erb_low_hz, erb_high_hz), ...
        'FontSize', 16, 'FontWeight', 'bold');

%% ========================================================================
%  Additional Visualization: ERB-band ILD Error Heatmap
% =========================================================================

figure('Name', 'ILD Error Across ERB Bands', 'Position', [150 150 1200 600]);
imagesc(azimuth_test, center_freqs_hz, abs(ILD_BSM_bands - ILD_reference_bands));
axis xy;
colorbar;
xlabel('Azimuth Angle \phi (degrees)', 'FontSize', 12);
ylabel('ERB Center Frequency (Hz)', 'FontSize', 12);
title('Absolute ILD Error per ERB Band', 'FontSize', 14, 'FontWeight', 'bold');
set(gca, 'YScale', 'log', 'FontSize', 11);

%% ========================================================================
%  Save Results
% =========================================================================

ild_results.azimuth_test = azimuth_test;
ild_results.elevation_test = elevation_test;
ild_results.center_freqs_hz = center_freqs_hz;
ild_results.ILD_reference_bands = ILD_reference_bands;
ild_results.ILD_BSM_bands = ILD_BSM_bands;
ild_results.ILD_reference_avg = ILD_reference_avg;
ild_results.ILD_BSM_avg = ILD_BSM_avg;
ild_results.ILD_error_avg = ILD_error_avg;
ild_results.parameters.num_erb_bands = num_erb_bands;
ild_results.parameters.erb_low_hz = erb_low_hz;
ild_results.parameters.erb_high_hz = erb_high_hz;
ild_results.parameters.M = M;
ild_results.parameters.Q = Q;
ild_results.parameters.SNR_dB = SNR_dB;
ild_results.parameters.fs = fs;

save('ILD_fig9_results.mat', 'ild_results');
fprintf('Results saved to: ILD_fig9_results.mat\n');

fprintf('\n=== ILD Analysis Complete! ===\n');


%% 转511 Harman json

pos(:,3)=0;
pos2(:,3) =pos2(:,3)/2;
pos1 = [pos;pos2];
[az, el, r] = cart2sph(pos1(:,1), pos1(:,2), pos1(:,3));
sph1 = [az, el, r];