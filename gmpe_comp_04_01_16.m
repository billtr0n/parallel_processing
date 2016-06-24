%%% normal parameters
% read these in from a file.
fid = fopen('params.txt');
line = fgets(fid);
while ischar(line)
    [key, val] = strread(line, '%s %s');
    val = char(val);
    if (numel(line) == 1); break; end;
    if (strcmp(key, 'nflt')   == 1); nflt       = sscanf(val, '%f'); end;
    if (strcmp(key, 'nx'  )   == 1); nx         = sscanf(val, '%f'); end;
    if (strcmp(key, 'ny'  )   == 1); ny         = sscanf(val, '%f'); end;
    if (strcmp(key, 'mw'  )   == 1); M         = sscanf(val, '%f'); end;
    if (strcmp(key, 'ft'  )   == 1); Fault_Type = sscanf(val, '%f'); end;
    if (strcmp(key, 'region') == 1); region     = sscanf(val, '%f'); end;
    if (strcmp(key, 'z1')     == 1); z1         = sscanf(val, '%f'); end;
    if (strcmp(key, 'Vs30')   == 1); Vs30       = sscanf(val, '%f'); end;
    if (strcmp(key, 'W')      == 1); W          = sscanf(val, '%f'); end;
    if (strcmp(key, 'Ztor')   == 1); Ztor       = sscanf(val, '%f'); end;
    if (strcmp(key, 'Zbot')   == 1); Zbot       = sscanf(val, '%f'); end;
    if (strcmp(key, 'F')      == 1); F          = sscanf(val, '%f'); end;
    if (strcmp(key, 'delta')  == 1); delta      = sscanf(val, '%f'); end;
    if (strcmp(key, 'lam')    == 1); lam        = sscanf(val, '%f'); end;
    if (strcmp(key, 'Fhw')    == 1); Fhw        = sscanf(val, '%f'); end;
    if (strcmp(key, 'Z25')    == 1); Z25        = sscanf(val, '%f'); end;
    if (strcmp(key, 'Zhyp')   == 1); Zhyp       = sscanf(val, '%f'); end;
    if (strcmp(key, 'FVS30')  == 1); FVS30      = sscanf(val, '%f'); end;
    if (strcmp(key, 'fas')    == 1); fas        = sscanf(val, '%f'); end;
    if (strcmp(key, 'Hw')     == 1); Hw         = sscanf(val, '%f'); end;
    if (strcmp(key, 'strtx')  == 1); strtx      = sscanf(val, '%f'); end;
    if (strcmp(key, 'strty')  == 1); strty      = sscanf(val, '%f'); end;
    line = fgets(fid);
end
        
%nflt = 1301
%nx = 2900
%ny = 1600
%M = 6.88
%Fault_Type = 1
%region = 1
%z1 = 0.00
%Vs30 = 1250.
%W = 17.0
%Ztor = 0.
%Zbot = 999.
%F = 0
%delta = 90.
%lam = 0.
%Fhw = 0.
%Z25 = 2.6 
%Zhyp = 10.0
%FVS30 = 0.
%fas = 0.
%Hw = 0.

% Load SORD mesh data 
M 
nflt
strtx

mean_fault_plane = 20000.0
sord_dx = 25.0
awp_dx = 25.0
gmpe_dx = 100.0
sim_output_dx = 50.0
len_gmpe_x = 1450
len_gmpe_y = 800 
nskpx_sim = 2
len_fault = nflt * 2
nskpx_gmpe = 4
awp_fault_offset_x = 1600
awp_fault_offset_y = 1600
%freq = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0]
freq = [1.0, 2.0, 3.0, 5.0]
period = 1.0 ./ freq

% cartesian coordinates from SORD -> Awp Mesh indices
mean_fault_ind = round(mean_fault_plane / sord_dx / nskpx_sim);
x3o = fread(fopen('./out/x3os','rb'),[1301,801],'single');
x1o = fread(fopen('./out/x1os','rb'),[1301,801],'single');

% 
%x3o = round((x3o(:,mean_fault_ind) - mean_fault_plane) / sord_dx) + awp_fault_offset_y; % convert to AWP-ODC mesh, x3o in model_dx not output_dx
%x1o = round(x1o(:,mean_fault_ind) / sord_dx) + awp_fault_offset_x + strtx; % convert to awp mesh
%[xx, yy] = meshgrid(1:nskpx_gmpe:nskpx_sim*nx, 1:nskpx_gmpe:nskpx_sim*ny); % decimate 

% it was confusing, just trying to keep everything in meters now
x3o = x3o(:,mean_fault_ind) - mean_fault_plane + awp_fault_offset_y * awp_dx;
x1o = x1o(:,mean_fault_ind) + awp_fault_offset_x * awp_dx;
[xx, yy] = meshgrid(1:gmpe_dx:len_gmpe_x*gmpe_dx, 1:gmpe_dx:len_gmpe_y*gmpe_dx); % decimate  
disp('Calculating distances...');
rjb = zeros(len_gmpe_y, len_gmpe_x)+1e100; % because nskpx = 2 and skpx_gmpe = 4, 'inf' is temp value for comparison
rx = zeros(len_gmpe_y, len_gmpe_x);
ry0 = zeros(len_gmpe_y, len_gmpe_x);

%% Compute Rx and Ry0 fault_start = 1600 in undecimated AWP coordintes
%fault_start = awp_fault_offset_x + strtx;
%fault_end = fault_start + len_fault;

%% convert strtx to same spatial resolution as fault location file (dx/2) <- but tehse we need in indeces
strtx = round(strtx/2);
endx = round(strtx/2) + nflt;
x1mt = ones(len_gmpe_y,len_gmpe_x);
x3mt = ones(len_gmpe_y,len_gmpe_x);
for i=strtx:endx
    x1m = x1mt * x1o(i);
    x3m = x3mt * x3o(i);
    euc_d = sqrt((xx-x1m).^2+(yy-x3m).^2);
    inds = euc_d < rjb;
    rjb(inds) = euc_d(inds);
end
%%for i=1:nx/2 % because we decimate teh comparison by 2 w/r/t to the SA output
    %%real_i = i * 4;
    %%if real_i <= fault_start
        %%rx(:,i) = rjb(:,fault_start); % convert from dx=25 to dx=100
        %%ry0(:,i) = abs(real_i-fault_start); 
    %%elseif real_i >= fault_end
        %%rx(:,i) = rjb(:,round(fault_end/4));
        %%ry0(:,i) = abs(real_i-fault_end);
    %%else
        %%rx(:,i) = rjb(:,i);
        %%ry0(:,i) = 0.0;
    %%end
%%end
fault_start = x1o(strtx);
fault_end = x1o(endx);
fault_start_ind = round(fault_start / gmpe_dx);
fault_end_ind = round(fault_end / gmpe_dx);
for i=1:len_gmpe_x % because we decimate teh comparison by 2 w/r/t to the SA output
    d = i * gmpe_dx;
    if d < fault_start
        rx(:,i) = rjb(:,fault_start_ind); % convert from dx=25 to dx=100
        ry0(:,i) = abs(i-fault_start_ind); 
    elseif d > fault_end
        rx(:,i) = rjb(:,fault_start_ind);
        ry0(:,i) = abs(i-fault_end_ind);
    else
        rx(:,i) = rjb(:,i);
        ry0(:,i) = 0.0;
    end
end

%% Convert to kilometers
rjb = rjb * 0.001;
rx = rx * 0.001;
ry0 = ry0 * 0.001;

figure()
imagesc(rjb)
colorbar()
print('rjb.pdf', '-dpdf')

figure()
imagesc(rx)
colorbar()
print('rx.pdf', '-dpdf')

figure()
imagesc(ry0)
colorbar()
print('ry0.pdf', '-dpdf')

%% Compute GMPE for each location in Mesh
med_gmpes = zeros(4,ny/2,nx/2);
sig_gmpes = zeros(4,ny/2,nx/2);
edges = [[0:1.0:30.0] inf];
med_min_gmpe = zeros(1, length(edges)-1);
med_max_gmpe = zeros(1, length(edges)-1);
sig_med_gmpe = zeros(1, length(edges)-1);
med_sim = zeros(1, length(edges)-1);

for k=1:length(period)
    disp(['Computing GMPEs for period ', num2str(period(k))]);
%%% OLD TECHNIQUE %%%%%%%%%%%%%%%%
    for j=1:nx/2
        for i=1:ny/2
            [m_bssa, sig_bssa, per] = BSSA_2014_nga(M, period(k), rjb(i,j), Fault_Type, region, z1, Vs30);
            [m_cb, sig_cb, per] = CB_2014_nga(M, period(k), rjb(i,j), rjb(i,j), rx(i,j), W, Ztor, Zbot, delta, lam, Fhw, Vs30, Z25, Zhyp, region);
            [m_cy, sig_cy, per] = CY_2014_nga(M, period(k), rjb(i,j), rjb(i,j), rx(i,j), Ztor, delta, lam, z1, Vs30, Fhw, FVS30, region);
            [m_ask, sig_ask, per] = ASK_2014_nga(M, period(k), rjb(i,j), rjb(i,j), rx(i,j), ry0(i,j), Ztor, delta, lam, fas, Hw, W, z1, Vs30, FVS30, region);
            
            % store median value
            med_gmpes(1,i,j) = m_bssa;
            med_gmpes(2,i,j) = m_cb;
            med_gmpes(3,i,j) = m_cy;
            med_gmpes(4,i,j) = m_ask;
            
            % store standard deviation
            sig_gmpes(1,i,j) = sig_bssa;
            sig_gmpes(2,i,j) = sig_cb;
            sig_gmpes(3,i,j) = sig_cy;
            sig_gmpes(4,i,j) = sig_ask;

        end
    end

    % alternate technique: Make array of unique distances. Calculate GMPE at those disatances, then take median, no need to repeat calculations.
    %[u,ia,ib] = unique(rjb);
    %length(ia)
    %rjb_gmpe = rjb(ia);
    %n_rjb_gmpe = length(rjb_gmpe);
    %for i=1:n_rjb_gmpe
        %[m_bssa, sig_bssa, per] = BSSA_2014_nga(M, period(k), rjb(i,j), Fault_Type, region, z1, Vs30);
        %[m_cb, sig_cb, per] = CB_2014_nga(M, period(k), rjb(i,j), rjb(i,j), rx(i,j), W, Ztor, Zbot, delta, lam, Fhw, Vs30, Z25, Zhyp, region);
        %[m_cy, sig_cy, per] = CY_2014_nga(M, period(k), rjb(i,j), rjb(i,j), rx(i,j), Ztor, delta, lam, z1, Vs30, Fhw, FVS30, region);
        %[m_ask, sig_ask, per] = ASK_2014_nga(M, period(k), rjb(i,j), rjb(i,j), rx(i,j), ry0(i,j), Ztor, delta, lam, fas, Hw, W, z1, Vs30, FVS30, region);
        
        %% store median value
        %med_gmpes(1,i,j) = m_bssa;
        %med_gmpes(2,i,j) = m_cb;
        %med_gmpes(3,i,j) = m_cy;
        %med_gmpes(4,i,j) = m_ask;
        
        %% store standard deviation
        %sig_gmpes(1,i,j) = sig_bssa;
        %sig_gmpes(2,i,j) = sig_cb;
        %sig_gmpes(3,i,j) = sig_cy;
        %sig_gmpes(4,i,j) = sig_ask;
    %end

    % Perform Distance Binning
    min_gmpe = squeeze(min(med_gmpes,[],1));
    max_gmpe = squeeze(max(med_gmpes,[],1));
    sig_gmpe = squeeze(median(sig_gmpes,1));

    fname = sprintf('./het/gmrotD50_%05.2fHz.dat', freq(k));
    sim_sa = reshape(importdata(fname),nx,ny)' / 9.81;
    sim_sa = sim_sa(1:2:end,1:2:end); % decimate by two to reduce computations
    % get counts and index of the bin each member of rjb sorts into.
    [bc,ind] = histc(rjb, edges);

    for i=1:length(edges)-1
        f_ind = find(ind == i);
        med_sim(i) = median(sim_sa(f_ind));
        med_min_gmpe(i) = median(min_gmpe(f_ind));
        med_max_gmpe(i) = median(max_gmpe(f_ind));
        sig_med_gmpe(i) = median(sig_gmpe(f_ind));
    end

    edges_plot = edges(1:end-1) + 0.5; % just moves it to the midpoint dumbly
    out = [edges_plot', med_sim', med_min_gmpe', med_max_gmpe', sig_med_gmpe'];
    fout = sprintf('seed40_gmrotD50_%05.2fHz_plot.dat',freq(k));
    csvwrite(fout,out)
end
