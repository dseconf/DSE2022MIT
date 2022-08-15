# NFXP class: Solves Rust's engine repplacement model Rust(Ecta, 1987) 

#import packages
import numpy as np
import time

class solve_NFXP():
    def __init__(self,**kwargs):
        self.setup(**kwargs)

    def setup(self,**kwargs):       #**kwargs means that it is optionally to include this input
 
        # Successive approximations step
        self.sa_max = 50      # Maximum number of contractions steps
        self.sa_min = 10      # Minimum number of contraction steps
        self.sa_tol = 1.0e-10 # Absolut toletance before

        # Newton-Kantorovich steps
        self.max_fxpiter = 5     # Maximum number of times to switch between Newton-Kantorovich iterations and contraction iterations.
        self.pi_max = 10         # Maximum number of Newton-Kantorovich steps

        self.pi_tol = 1.0e-12    # Final exit tolerance in fixed point algorithm, measured in units of numerical precision
        self.tol_ratio = 1.0e-02 # Relative tolerance before switching to N-K algorithm when discount factor is supplied as input in solve.poly
        self.printfxp = 0        # Print iteration (0= no output), (1=compressed output), (2= detailed iteraion output)

        #If kwargs exist
        for key,val in kwargs.items():
            setattr(self,key,val) 

    def poly(self,bellman, V0=np.zeros(1), beta= 0.0, output=1):

        t0poly = time.time()  # set the starting time

        for k in range(self.max_fxpiter):

            # 1. CONTRACTION ITERATIONS (S-A)
            if self.printfxp>0:
                print(f'Begin contraction iterations (for the {k+1} time)')
            V0,iter_sa= self.sa(bellman,V0,beta)

            # 2. NEWTON-KANTOROVICH ITERATIONS
            if self.printfxp>0:
                print(f'Begin Newton-Kantorovich iterations (for the {k+1} time)')
            V0,pk,dV, iter_nk = self.nk(bellman,V0)


            t1poly = time.time()
            if iter_nk.converged=='true':
                if self.printfxp>0:
                    print(f'Convergence achieved!')
                    print(f'Elapsed time: {(t1poly-t0poly):.4f} (seconds)')
                    break 
            else:
                if k >= self.max_fxpiter:
                    print(f'No convergence! Maximum number of iterations exceeded without convergence!')
                    break
        V = V0
        if output==1:            
            return V
        if output==2:            
            return V, pk
        if output==3:            
            return V, pk, dV
        if output==5:            
            return V, pk, dV, iter_sa, iter_nk
        else:
            print('solve_NFXP.poly: output must be 1,2,3 or 5')

    def sa(self,bellman,V0=np.zeros(1), beta=0.0):
        
        # Solve for fixed point using successive approximations
        class iteration: pass
        t0 = time.time()  # set the starting time
        iteration.tol = np.nan+np.zeros((self.sa_max))
        iteration.rtol = np.nan+np.zeros((self.sa_max))
        iteration.converged = 'false'
        for i in range(self.sa_max):
            V = bellman(V0,output=1)
            iteration.tol[i] = max(abs(V-V0))
            V0 = V.copy()

            # Stopping criteria 1
            adj  = np.ceil(np.log10(abs(max(V0))))
            ltol = self.sa_tol*10**adj  # Adjust final tolerance
            if (i<=self.sa_min) and (iteration.tol[i]<ltol):
                iteration.message = "SA converged after {} iterations, tolerance: {:.4g}".format(i,iteration.tol[i])
                iteration.converged = 'true'
                break

            # Stopping criteria 2
            iteration.rtol[i] = iteration.tol[i]/iteration.tol[max(i-1,0)]
            if (i<=self.sa_min) and (abs(beta-iteration.rtol[i]) < self.tol_ratio):
                iteration.message = 'SA stopped prematurely due to relative tolerance. Start NK iterations'
                break
        
        iteration.n = i+1
        iteration.tol = iteration.tol[0:i+1]
        iteration.rtol = iteration.rtol[0:i+1]
        t1 = time.time()            # set the ending time
        iteration.time = t1-t0 

        self.print_output(iteration)

        return V, iteration

    def nk(self,bellman, V0):
        class iteration: pass
        t0 = time.time()
        iteration.tol =  np.nan+np.zeros((self.pi_max))
        iteration.rtol = np.nan+np.zeros((self.pi_max))
        iteration.converged = 'false'

        m = V0.size

        for i in range(self.pi_max):

            # Do N-K step
            V1, pk, dV = bellman(V0,output=3)
            F = np.eye(m)-dV
            V = V0 - np.linalg.inv(F) @ (V0 - V1) 
            
            # do additional SA iteration for stability and accurate measure of error bound
            V0 = bellman(V,output=1)

            # Tolerance
            iteration.tol[i]=max(abs(V-V0))
            iteration.rtol[i] = iteration.tol[i]/(iteration.tol[max(i-1,0)] + 1.0e-15)      

            #Adjust 
            adj  = np.ceil(np.log10(abs(max(V0))))
            ltol = self.pi_tol*10**adj  # Adjust final tolerance

            if iteration.tol[i] < ltol:
                #Convergence achieved
                iteration.message = "N-K converged after {} iterations, tolerance: {:.4g}".format(i+1,iteration.tol[i])
                iteration.converged = 'true'
                break
        
        iteration.n = i+1
        iteration.tol = iteration.tol[0:i+1]
        iteration.rtol = iteration.rtol[0:i+1]
        t1 = time.time()
        iteration.time = t1-t0 

        self.print_output(iteration)

        return V, pk, dV, iteration

    def print_output(self,iteration):
        if self.printfxp>1:           #print detaled output
            for i,iter_tol in enumerate(iteration.tol):
                print(f'Iteration {i+1}, tol {iter_tol:10.4g}, tol(j)/tol(j-1) {iteration.rtol[i]:10.4g}')

        if self.printfxp>0:           # print final output
            if iteration.converged == 'true':
                print(f'{iteration.message}')
            else:
                print(f'Maximum number of iterations reached, tolerance: {iteration.tol[-1]:.4f}')
            print(f'Elapsed time {iteration.time:.4f} seconds')
        