/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm_m.blockentity.machines;

/**
 * N-01/N-05 boundary: implement ONLY on a research-reactor core whose simulation
 * supplies O's current totalFlux. This is a read-only server-side query; it does
 * not store, generate, transfer or consume neutrons. The breeder reads horizontal
 * contacts (including controller-resolved multiblock parts) each server tick.
 * The current generic reactor_small block supplies no flux and remains N-05 work.
 */
public interface ResearchReactorFluxSource {
    int getTotalFlux();
}
