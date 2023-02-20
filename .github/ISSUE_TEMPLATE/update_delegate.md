---
name: Update delegate data
about: Request to update delegate data
title: "[Delegates] "
labels: infrastructure
assignees: ''

---

# Environment
- [ ] staging
- [ ] production

# Action
- [ ] update data
- [ ] remove delegate

# Current delegate data:
- name: [name],
- address: [address],
- ens: [ens],
- image_url: [image_url],
- reason: [reason],
- contribution: [contribution]

# Change delegate data to (if updating):
- name: [name],
- address: [address],
- ens: [ens],
- image_url: [image_url],
- reason: [reason],
- contribution: [contribution]

# Acceptance Criteria
- [ ] Update:
  - [ ] Delegate has a name.
  - [ ] Provided address is valid.
  - [ ] If ens name is available it can be resolved to a valid address.
  - [ ] Provided image can be fit into a square placeholder. Too long or too wide images are not acceptable.
  - [ ] Reason for becoming a delegate is provided (not empty). 
  - [ ] Previous contribution is provided (not empty).
- [ ] Delete:
  - [ ] All delegate data is removed

# Optional comments
