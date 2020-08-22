# ansible_homelab
Ansible playbooks and code to operate my homelab

## Role docs
  * lh_new_ipdns
    * Reserves a new IP and creates DNS records
	* expects a var of new_vm_name and returns newip
  * rmdns
    * Deletes a DNS record
	* expects a var of cur_name
