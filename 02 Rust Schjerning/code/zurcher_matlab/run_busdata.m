% run_busdata: Estimates Rust's engine replacement model using the Bus data from Rust(Ecta, 1987) 
% Methods used in this script: NFXP full mle
% clear

% methods to cosinder
method={'nfxp (pmle)', 'nfxp (mle)'}; 
% method={'nfxp (mle)', 'nfxp (pmle)', 'mpec (pmle)'}; % available:  

% Set parameters (values for RC and mp.c will be used as starting values during estimation)
mp0.RC=0;     				% Replacement cost
mp0.c=0;					% Cost parameter
mp0.n=175;					% Number of grid-points
mp0.bellman_type='ev';  	% bellman in expected value ('ev') or ('iv') integrated value function space  
mp0.pnames_u={'RC', 'c'};	% utility parameters to be estimated
mp0.pnames_P={'p'};         % set mp0.pnames_P={}; to skip estimation of transition parameters  
mp0.bustypes=[1,2,3,4];		% Vector with chosen bus types (elements can be 1,2,3,4) 

% Fill out remaining parameters and update parameter dependencies
mp=zurcher.setup(mp0);

% Read data
data = zurcher.readbusdata(mp);

for i=1:numel(method)
	switch method{i}
		case 'nfxp (mle)'
			% Full MLE using NFXP implementation
			mp.pnames_P={'p'};
			[results, theta_hat, Avar]=nfxp.estim(data, mp);
		case 'nfxp (pmle)'
			% Two step partial MLE using NFXP
			mp.pnames_P={};
			[results, theta_hat, Avar]=nfxp.estim(data, mp);
		case 'mpec (pmle)'
			% Two step partial MLE using MPEC
			mp.pnames_P={};
			[results, theta_hat, Avar]=mpec.estim(data, mp);
		otherwise
			error('Method does not exist');
	end

	% ************************************
	% Print output
	% ************************************

	if i==1	
		fprintf('Structural Estimation using busdata from Rust(1987)\n');
		fprintf('Bustypes       = ['); fprintf(' %d ',mp.bustypes); fprintf(']\n');
		fprintf('Beta           = %10.5f \n',mp.beta);
		fprintf('n              = %10.5f \n',mp.n);
		fprintf('Sample size    = %10.5f \n',numel(data.d));
		fprintf('\n'); 
	end
	fprintf('\n'); 

	fprintf('\nMethod %s\n', method{i});
	output.estimates(results, [mp.pnames_u mp.pnames_P], theta_hat, Avar);
	fprintf('log-likelihood    = %10.5f \n',results.llval);
	fprintf('runtime (seconds) = %10.5f \n',results.cputime);
	if isfield(results,'grad_direc') 
		fprintf('g''*inv(h)*g      = %10.5e \n',results.grad_direc);
	end
end








