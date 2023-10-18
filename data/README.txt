Hello JOSS Reviewers,

I present a straightforward dataset designed for testing the LIBSsa software. The dataset is organized into the following sections:

    Samples
    1.1. Leaves
        These samples were gathered using a High-Resolution Spectrometer and are intended for plasma temperature calculation using the Saha-Boltzmann plot.
    1.2. Soils and Leaves
        Collected with a Low-Resolution Spectrometer, these samples are suitable for Principal Component Analysis (PCA) clustering, owing to the varying matrices.
    1.3. Synthetic Samples
        Acquired using an Ultra-Low-Resolution Spectrometer, these samples are well-suited for developing Carbon linear models.

    Parameters
    2.1. Carbon References.xlsx
        This file can be imported into the program to compute C linear models. To ensure accurate modeling, focus on isolating the C peak, which is located near or around 247.8 nm.
    2.2. Ti Iso Table.xlsx
        This file can assist in isolating specific Ti lines for use in the Saha-Boltzmann plot.
    2.3. Ti TNe Table.xlsx
        Import this file before conducting the Saha-Boltzmann plot, after isolating Ti peaks and calculating their areas. It contains detailed data that may require laborious extraction from the NIST Atomic Spectra Database.

---

In addition to these files, I have included a set of screenshots that illustrate various aspects of using the LIBSsa software with synthetic samples (KBr+Graphite):

    Screenshot 1: Loading Spectra
        This screenshot demonstrates how to load spectra into the software for analysis.

    Screenshot 2: Outliers Removal
        How apply outliers removal from the data with.

    Screenshot 3: Peak Isolation
        The process of isolating peaks within the spectra for further analysis.

    Screenshot 4: Peak Fitting
        This screenshot provides instructions for fitting peaks to the data accurately.

    Screenshot 5: Linear Models
        Finally, how to create and apply linear models to samples using the software.

These screenshots are included to help reviewers navigate the software effectively. Please let me know if you need any additional information or have any questions.
