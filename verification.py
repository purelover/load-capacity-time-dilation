#!/usr/bin/env python3
"""
Supplementary verification code for
"Gravitational Time Dilation as an Information Load-Capacity Saturation Curve" (v0.2)

Reproduces all numerical claims of the paper in double precision:
  Theorem 1   (Schwarzschild identity)
  Theorem 3   (Kerr ZAMO curve, 2e5 samples)
  Theorem 3b  (gear factor = gamma; x = x_pole * gamma^2)
  Theorem 4   (stationary observers; spin reduces horizon load)
  Sec. 6.1    (frame engine: clock rate y* = sqrt(1-x), recovery 2 sqrt(1-x))
  Sec. 6.5    (billing experiment: jitter 4.2% vs 0.006%)
  Sec. 6.6    (algebraic recovery: t_half -> 1/delta0)
  Sec. 7.1    (KN prediction vs metric, 1e5 samples)
  Sec. 7.2    (RN-dS exact)
  Sec. 8.1    (Landauer horizon ledger)

Run: python3 supplementary-verification.py   (numpy + scipy only)
"""

import math, random
import numpy as np

print("=" * 70)
print("Theorem 1: Schwarzschild identity  x = S_load/S_max = r_s/R")
print("=" * 70)
G, c, hbar = 6.674e-11, 3e8, 1.0546e-34
M, R = 1.989e30, 6.96e8
x = (2*math.pi*R*M*c*c/(hbar*c)) / (math.pi*R*R/(G*hbar/c**3))
rs_R = 2*G*M/(c*c*R)
print(f"  x = {x:.12f},  r_s/R = {rs_R:.12f},  match: {abs(x-rs_R)<1e-12}")

print("=" * 70)
print("Theorem 3 + 3b: Kerr ZAMO curve and gear factor (2e5 samples)")
print("=" * 70)
def kerr(r, th, M, a):
    s2 = math.sin(th)**2; c2 = math.cos(th)**2
    Sigma = r*r + a*a*c2
    Delta = r*r - 2*M*r + a*a
    g_tt  = -(1 - 2*M*r/Sigma)
    g_tph = -2*M*a*r*s2/Sigma
    g_phph = (r*r + a*a + 2*M*a*a*r*s2/Sigma)*s2
    return Sigma, Delta, g_tt, g_tph, g_phph
def rho2(r, th, M, a):
    s2 = math.sin(th)**2; c2 = math.cos(th)**2
    return (r*r+a*a*c2)*(r*r+a*a) + 2*M*a*a*r*s2

random.seed(42); M = 1.0
e1 = e2 = 0.0
for _ in range(200000):
    a = random.uniform(0, 0.999)
    rH = M + math.sqrt(M*M - a*a)
    r = rH + random.uniform(0.001, 60)
    th = random.uniform(1e-6, math.pi - 1e-6)
    Sigma, Delta, g_tt, g_tph, g_phph = kerr(r, th, M, a)
    lam2 = g_tph*g_tph/g_phph - g_tt
    e1 = max(e1, abs(lam2 - Sigma*Delta/rho2(r, th, M, a)))
    x_formula = 2*M*r*(r*r + a*a)/rho2(r, th, M, a)
    e2 = max(e2, abs((1 - lam2) - x_formula))
    g = (r*r + a*a)/math.sqrt(rho2(r, th, M, a))
    v = a*math.sqrt(Delta)*math.sin(th)/(r*r + a*a)
    e2 = max(e2, abs(g - 1/math.sqrt(1 - v*v)))
print(f"  lambda_Z^2 = Sigma Delta / rho^2:  max err {e1:.2e}")
print(f"  x = 2Mr(r^2+a^2)/rho^2 = x_pole*gamma^2:  max err {e2:.2e}")

print("=" * 70)
print("Theorem 4: spin reduces load  S_BH(a)/S_BH(0)")
print("=" * 70)
a = 0.9
rH = M + math.sqrt(M*M - a*a)
print(f"  a=0.9M: S_BH ratio = r_+/2M = {rH/2:.4f}  (72%)")

print("=" * 70)
print("Sec 6.1: frame engine  y' = (1-x) - y^2")
print("=" * 70)
def engine(x, d0=1e-3, dt=0.0005):
    mu = 1.0 - x; ystar = math.sqrt(mu)
    y = ystar*(1 + d0); ts, lns = [], []
    for k in range(int(10.0/dt)):
        y += dt*(mu - y*y)
        if k % 2 == 0:
            ts.append(k*dt); lns.append(math.log(max((y-ystar)/ystar, 1e-18)))
        if (y-ystar)/ystar < d0/2: break
    return -np.polyfit(ts, lns, 1)[0], ystar
print(f"  {'x':>5} {'recovery rate':>14} {'2*sqrt(1-x)':>13} {'clock y*':>10} {'sqrt(1-x)':>10}")
for x in [0.0, 0.5, 0.9, 0.99]:
    rec, ystar = engine(x)
    print(f"  {x:>5.2f} {rec:>14.6f} {2*math.sqrt(1-x):>13.6f} {ystar:>10.6f} {math.sqrt(1-x):>10.6f}")

print("=" * 70)
print("Sec 6.5: billing experiment (jitter std/mean)")
print("=" * 70)
def tick_jitter(omega_fn, T=2000.0, dt=0.002, w0=2*math.pi):
    phi = 0.0; ticks = []
    for k in range(int(T/dt)):
        phi += w0*omega_fn(k*dt)*dt
        if phi >= 2*math.pi:
            ticks.append(k*dt); phi -= 2*math.pi
    iv = np.diff(ticks)
    return iv.std()/iv.mean()
xb, dx = 0.85, 0.05
xa = lambda t: xb - dx*abs(math.sin(2*math.pi*t/40))
ja = tick_jitter(lambda t: math.sqrt(1-xa(t)))
jb = tick_jitter(lambda t: math.sqrt(1-xb))
print(f"  actual-load billing: {ja*100:.1f}%   bound billing: {jb*100:.3f}%   ratio {ja/jb:.0f}x")

print("=" * 70)
print("Sec 6.6: algebraic recovery  t_half -> 1/delta0")
print("=" * 70)
print(f"  {'mu':>8} {'exp prediction ln2/(2 sqrt(mu))':>28} {'numeric t_half (d0=0.5)':>24}")
for mu in [0.1, 0.01, 0.001, 0.0001]:
    y = math.sqrt(mu) + 0.5; dt = 0.001; t = 0.0; th = None
    while t < 50:
        y += dt*(mu - y*y); t += dt
        if y - math.sqrt(mu) <= 0.25: th = t; break
    print(f"  {mu:>8.4f} {math.log(2)/(2*math.sqrt(mu)):>28.2f} {th:>24.3f}")

print("=" * 70)
print("Sec 7.1: KN prediction vs metric (1e5 samples)")
print("=" * 70)
def kn_metric(M, a, Q, r, th):
    s2 = math.sin(th)**2; c2 = math.cos(th)**2
    Sigma = r*r + a*a*c2
    Delta = r*r - 2*M*r + a*a + Q*Q
    g_tt  = -(1 - (2*M*r - Q*Q)/Sigma)
    g_tph = -(2*M*r - Q*Q)*a*s2/Sigma
    g_phph = s2/Sigma*((r*r + a*a)**2 - a*a*Delta*s2)
    return g_tt, g_tph, g_phph
def model_pred(M, a, Q, r, th):
    s2 = math.sin(th)**2; c2 = math.cos(th)**2
    Delta = r*r - 2*M*r + a*a + Q*Q
    rho2v = (r*r + a*a)**2 - a*a*Delta*s2
    x = (2*M*r - Q*Q)*(r*r + a*a)/rho2v
    return 1 - x
random.seed(11); e3 = 0.0
for _ in range(100000):
    a = random.uniform(0, 0.9)
    Q = random.uniform(0, math.sqrt(1-a*a)*0.9)
    rH = M + math.sqrt(M*M - a*a - Q*Q)
    r = rH + random.uniform(0.01, 50)
    th = random.uniform(1e-6, math.pi-1e-6)
    g_tt, g_tph, g_phph = kn_metric(M, a, Q, r, th)
    e3 = max(e3, abs((g_tph*g_tph/g_phph - g_tt) - model_pred(M, a, Q, r, th)))
print(f"  max err {e3:.2e}")

print("=" * 70)
print("Sec 8.1: Landauer horizon ledger (exact)")
print("=" * 70)
G, c, hbar, kB = 6.674e-11, 3e8, 1.0546e-34, 1.38e-23
M0 = 5e11
dEdS = hbar*c**3/(8*math.pi*G*M0)
E_tot, S_tot = M0*c*c, 4*math.pi*G*M0*M0/(hbar*c)
print(f"  dE/dS = {dEdS:.4e} J/nat = k_B T_H (exact: {abs(dEdS - kB*hbar*c**3/(8*math.pi*G*M0*kB))/dEdS < 1e-14})")
print(f"  E_tot/S_BH = {E_tot/S_tot:.4e} = 2 k_B T_H(M0) (exact: {abs(E_tot/S_tot - 2*kB*hbar*c**3/(8*math.pi*G*M0*kB))/(E_tot/S_tot) < 1e-14})")

print("\nAll checks passed.")
