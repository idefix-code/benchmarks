/* ///////////////////////////////////////////////////////////////////// */
/*!
  \file
  \brief Orszag-Tang MHD vortex.

  The Orszag Tang vortex system describes a doubly periodic fluid
  configuration leading to two-dimensional supersonic MHD turbulence.
  Although an analytical solution is not known, its simple and reproducible
  set of initial conditions has made it a widespread benchmark for
   inter-scheme comparison.

  The computational domain is the periodic box \f$[0,2\pi]^D\f$ where
  \c D is the number of spatial dimensions.
  In 2D, the initial condition is given by
  \f[
     \vec{v} = \left(-\sin y,\, \sin x, 0\right) \,,\qquad
     \vec{B} = \left(-\sin y,\, \sin 2x, 0\right) \,,\qquad
     \rho = 25/9\,,\qquad
     p    = 5/3
  \f]

  This test problem does not have any input parameter.

  A snapshot of the solution on a \c 512x512 grid is shown below.

  \image html mhd_ot.02.jpg "Density at t=3.1 (configuration #02)."

  \author A. Mignone (mignone@ph.unito.it)
  \date   April 13, 2014

  \b References
     - "Comparison of some Flux Corrected Transport and TVD numerical
        schemes for hydrodynamic and magnetohydrodynamic problems",
        Toth & Odstrcil, JCP (1996) 128, 82
     - "High-order conservative finite difference GLM-MHD schemes for
        cell-centered MHD", Mignone, Tzeferacos & Bodo, JCP (2010) 229, 5896.
*/
/* ///////////////////////////////////////////////////////////////////// */
#include "pluto.h"

/* ********************************************************************* */
void Init (double *us, double x1, double x2, double x3)
/*
 *
 *********************************************************************** */
{
  double x=x1, y=x2 ,z=x3;

  double B0 = 1.0/sqrt(4.0*M_PI);
  us[VX1] = - sin(2.0*M_PI*y);
  us[VX2] =   sin(2.0*M_PI*x) + cos(2.0*M_PI*z);
  us[VX3] =   cos(2.0*M_PI*x);

  us[BX1] = - sin(y);
  us[BX2] =   sin(2.0*x);
  us[BX3] = 0.0;
  us[RHO] = 25./(36.0*M_PI);
  #if EOS != ISOTHERMAL && EOS != BAROTROPIC
   us[PRS] = 5/(12.0*M_PI);
  #endif

  us[AX1] = B0/(2.0*M_PI)*cos(2.0*M_PI*y);
  us[AX2] = B0/(2.0*M_PI)*sin(2.0*M_PI*x);
  us[AX3] = B0/(2.0*M_PI)*(cos(2.0*M_PI*y) + 0.5*cos(4.0*M_PI*x));

}

/* ********************************************************************* */
void InitDomain (Data *d, Grid *grid)
/*!
 * Assign initial condition by looping over the computational domain.
 * Called after the usual Init() function to assign initial conditions
 * on primitive variables.
 * Value assigned here will overwrite those prescribed during Init().
 *
 *
 *********************************************************************** */
{
}



/* ********************************************************************* */
void Analysis (const Data *d, Grid *grid)
/*
 *
 *
 *********************************************************************** */
{
}
/* ********************************************************************* */
void UserDefBoundary (const Data *d, RBox *box, int side, Grid *grid)
/*
 *
 *
 *********************************************************************** */
{
}
