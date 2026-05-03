r"""
Propagation animation
=====================

Generate an animation of the propagation of impedance shift along axons' membrane



"""

import nrv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# %%
# Step 1: simulate axons
# ^^^^^^^^^^^^^^^^^^^^^^
#
# Two axons are simulated for 5ms:
#
# - A 10um large mylielinated axon of 33 node lenght
# - A 1um large unmylielinated axon of lenght 2300um
#
# In both simulations a current clamp is triggered at t=1ms in the axon' central position along x


def maxon_sim():
    """
    simulate a myelinated axon
    """
    Nseg = 3
    y = 0
    z = 0
    d = 6
    L = nrv.get_length_from_nodes(d, 33)

    axon = nrv.myelinated(
        y, z, d, L, dt=0.005, rec="all", Nseg_per_sec=Nseg - 1, model="MRG"
    )

    t_start = 1
    duration = 0.1
    amplitude = 2
    position = 0.5
    axon.insert_I_Clamp(position, t_start, duration, amplitude)

    t_sim = 5
    results = axon.simulate(
        t_sim=t_sim, record_V_mem=False, record_g_mem=True, record_g_ions=True
    )

    del axon
    return results


def uaxon_sim():
    Nseg = 2
    y = 0
    z = 0
    d = 1
    L = 2300

    axon = nrv.unmyelinated(y, z, d, L, dt=0.005, Nsec=3000)

    t_start = 1
    duration = 0.1
    amplitude = 2
    position = 0.5
    axon.insert_I_Clamp(position, t_start, duration, amplitude)

    t_sim = 5
    results = axon.simulate(t_sim=t_sim, record_V_mem=False, record_g_mem=True)

    del axon
    return results


# %%
# Step 2: Generate the animation
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# .. note::
#       The animation can be saved in a .mp4 file or a .gif by seting ``save_fig`` to ``True``

save_fig = False

if __name__ == "__main__":

    nrv.info()

    resultsm = maxon_sim()
    resultsu = uaxon_sim()
    xu = resultsu["x_rec"]
    gu = resultsu["g_mem"]  # shape (n_x, n_t)
    tu = resultsu["t"]

    xm = resultsm["x_rec"]
    gm = resultsm["g_mem"]  # shape (n_x, n_t)
    tm = resultsm["t"]
    dt = float(tm[1] - tm[0])

    # downsample frames if there are many timepoints
    max_frames = 400
    step = max(1, len(tm) // max_frames)
    frame_indices = list(range(0, len(tm), step))
    interval_ms = dt * 1000 * step  # ms between frames
    fps = 500.0 / interval_ms

    fig, axs = plt.subplots(2, figsize=(10, 5), layout="constrained")
    (lineu,) = axs[0].plot(xu, gu[:, frame_indices[0]], color="C0")
    axs[0].set_xlim(xu.min(), xu.max())
    axs[0].set_ylim(np.nanmin(gu), np.nanmax(gu))
    axs[0].set_xlabel("x-position")
    axs[0].set_ylabel("g_mem")
    titleu = axs[0].set_title(f"Unmyelinated axon")

    (linem,) = axs[1].plot(xm, gm[:, frame_indices[0]], color="C0")
    axs[1].set_xlim(xm.min(), xm.max())
    axs[1].set_ylim(np.nanmin(gm), np.nanmax(gm))
    axs[1].set_xlabel("x-position")
    axs[1].set_ylabel("g_mem")
    titlem = axs[1].set_title(f"Myelinated axon")

    mtime_text = axs[0].text(0.05, 0.9, "", transform=axs[0].transAxes)
    utime_text = axs[1].text(0.05, 0.9, "", transform=axs[1].transAxes)

    def update_frame(frame_idx, ax=axs):
        i = frame_indices[frame_idx]
        lineu.set_ydata(gu[:, i])
        linem.set_ydata(gm[:, i])

        utime_text.set_text(f"time = {tu[i]:.2f} s")
        mtime_text.set_text(f"time = {tu[i]:.2f} s")
        return (lineu, linem, utime_text, mtime_text)

    ani = animation.FuncAnimation(
        fig,
        update_frame,
        frames=len(frame_indices),
        interval=interval_ms * 2,
        blit=True,
    )

    if save_fig:
        output_gif = "g_mem.gif"
        writer = animation.PillowWriter(fps=fps)
        ani.save(output_gif, writer=writer)
        print(f"Saved animation to {output_gif}")

    plt.show()
