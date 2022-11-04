---
name: Update guardian data
about: Request to update guardian data
title: "[Guardians] "
labels: infrastructure
assignees: ''

---

# Environment
- [ ] staging
- [ ] production

# Action
- [ ] update data
- [ ] remove guardian

# Current guardian data:
- name: [name],
- address: [address],
- ens: [ens],
- image_url: [image_url],
- reason: [reason],
- contribution: [contribution]

# Change guardian data to (if updating):
- name: [name],
- address: [address],
- ens: [ens],
- image_url: [image_url],
- reason: [reason],
- contribution: [contribution]

# Acceptance Criteria
- [ ] Update:
  - [ ] Guardian has a name.
  - [ ] Provided address is valid.
  - [ ] If ens name is available it can be resolved to a valid address.
  - [ ] Provided image can be fit into a square placeholder. Too long or too wide images are not acceptable.
  - [ ] Reason for becoming a guardian is provided (not empty). 
  - [ ] Previous contribution is provided (not empty).
- [ ] Delete:
  - [ ] All guardian data is removed

# Optional comments
