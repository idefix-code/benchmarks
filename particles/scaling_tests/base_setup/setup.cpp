#include "idefix.hpp"
#include "setup.hpp"

bool haveParticles {false};
real PM; // particle mass
int perCell {-1};

Setup::Setup(Input &input, Grid &grid, DataBlock &data, Output &output) {
  haveParticles = input.Get<bool>("Setup", "haveParticles", 0);
  if(!haveParticles) return;

  if(input.Get<std::string>("Particles", "count", 0).compare("per_cell")!=0) {
    IDEFIX_ERROR("this setup requires initial particle count to use 'per_cell' mode");
  }

  perCell = input.Get<int>("Particles", "count", 1);

  // compute particle mass
  real totalGasMass = 0.22104853207207678; // fragile, should be computed
  auto nx1 = input.Get<int>("Grid", "X1-grid", 2);
  auto nx2 = input.Get<int>("Grid", "X2-grid", 2);
  auto nx3 = input.Get<int>("Grid", "X3-grid", 2);
  // we assume that the grid is purely uniform in res and that the box size is 1^3
  real cellMass = totalGasMass / nx1 / nx2 / nx3;
  auto ratio = input.Get<real>("Setup", "particles_to_gas_mass_ratio", 0);

  PM = cellMass * ratio / perCell;
}


void Setup::InitFlow(DataBlock &data) {
    // Create a host copy
    DataBlockHost d(data);
    real x,y,z;

    real B0=1.0/sqrt(4.0*M_PI);

    for(int k = 0; k < d.np_tot[KDIR] ; k++) {
        for(int j = 0; j < d.np_tot[JDIR] ; j++) {
            for(int i = 0; i < d.np_tot[IDIR] ; i++) {
                x=d.x[IDIR](i);
                y=d.x[JDIR](j);
                z=d.x[KDIR](k);

                d.Vc(RHO,k,j,i) = 25.0/(36.0*M_PI);
                d.Vc(PRS,k,j,i) = 5.0/(12.0*M_PI);
                d.Vc(VX1,k,j,i) = -sin(2.0*M_PI*y);
                d.Vc(VX2,k,j,i) = sin(2.0*M_PI*x)+cos(2.0*M_PI*z);
                d.Vc(VX3,k,j,i) = cos(2.0*M_PI*x);

                d.Vs(BX1s,k,j,i) = -B0*sin(2.0*M_PI*y);
                d.Vs(BX2s,k,j,i) = B0*sin(4.0*M_PI*x);
                d.Vs(BX3s,k,j,i) = B0*(cos(2.0*M_PI*x)+sin(2.0*M_PI*y));

            }
        }
    }

    if(haveParticles) {
      idfx::cout << "individual particle mass is " << PM << std::endl;
      // randomized initial positions and velocities
      for(int k = 0; k < d.PactiveCount; k++) {
        d.Ps(PX1,k) = d.xbeg[IDIR] + idfx::randm() * (d.xend[IDIR] - d.xbeg[IDIR]);
        d.Ps(PX2,k) = d.xbeg[JDIR] + idfx::randm() * (d.xend[JDIR] - d.xbeg[JDIR]);
        d.Ps(PX3,k) = d.xbeg[KDIR] + idfx::randm() * (d.xend[KDIR] - d.xbeg[KDIR]);
        d.Ps(PVX1,k) = 2e-3 * (0.5 - idfx::randm());
        d.Ps(PVX2,k) = 2e-3 * (0.5 - idfx::randm());
        d.Ps(PVX3,k) = 2e-3 * (0.5 - idfx::randm());

        d.Ps(PMASS,k) = PM;
      }
    }
    // Send it all, if needed
    d.SyncToDevice();
}

// Analyse data to produce an output
void MakeAnalysis(DataBlock & data) {}
