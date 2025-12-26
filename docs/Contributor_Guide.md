# 👷 Contributor Guide

## Before you commit code, verify the following:

### 1. The Labeling Check
* **Question:** Does this new dataset have a clear source and error margin?
* **Action:** If No, reject it. We do not ingest "unknown" data.
* **Action:** Ensure the `epistemic_status` column is populated correctly.

### 2. The Reference Frame Check
* **Question:** Is this motion defined in absolute coordinates (x,y,z)?
* **Action:** If Yes, reject it. Motion must be relative to a parent node (e.g., Earth relative to Sun).

### 3. The Narrative Check
* **Question:** Is the "Why" explained?
* **Action:** Any new visual feature must have a corresponding Wiki entry or 3D Label.

### 4. The "Frankenstein" Warning
* Do not add features just because they look cool. 
* If a feature violates the **Constitution** (e.g., seamless blending of real and fake data), it must be rejected.
