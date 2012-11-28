function [k, B] = hw2at(Family, Field, Value, DeviceList, Energy, BranchFlag)
%HW2AT - Converts control system values to simulator values
%  [K, B] = bts2at(Family, Field, Value, DeviceList, Energy, BranchFlag)
%
%  INPUTS
%  1. Family - Family name
%  2. Field - Sub-field (like 'Setpoint')
%  3. Value - Controls system values
%  4. DeviceList - Device list (Value and DeviceList must have the same number of rows)
%  5. Energy - Energy in GeV {Default: getenergy}
%              If Energy is a vector, each output column will correspond to that energy.
%              Energy can be anything getenergy accepts, like 'Model' or 'Online'.
%              (Note: If Energy is a vector, then Value can only have 1 column)
%  6. BranchFlag - 1 -> Lower branch
%                  2 -> Upper branch
%
%  OUTPUTS
%  1. K and B - K-value and field in AT convention
%     For dipole:      K = B / Brho
%     For quadrupole:  K = B'/ Brho
%     For sextupole:   K = B"/ Brho / 2
%

if nargin < 3
    error('At least 3 input required');
end

if isempty(Field)
    Field = 'Setpoint';
end

k = Value;
B = Value;
return

