# ansible_homelab
Ansible playbooks and code to operate my homelab

## Role docs
  * lh_new_ipdns
    * Reserves a new IP and creates DNS records
	* expects a var of new_vm_name and returns newip
  * rm_dns
    * Deletes a DNS record
	* expects a var of cur_name
  * rm_ip
    * Delete an IP from netbox
	* expects ip_to_delete
  * cname
	* Create new CNAME (all variables are short hostname, NOT FQDN)
	* new_cname: new name
	* new_cname_dest: A record to point new_cname to
  * configure_cisco_switch
    * Configures a cisco switch from netbox data
  * configure_eos_switch
    * Configures an Arisa switch from netbox data
  * letsencrypt_generate
    * Generate a new cert from letsencrypt
  * letsencrypt_push
    * Push a cert out to my hosts
  * network_settings
    * Gather settings for my network from netbox
	* Currently hardcodes some stuff in vars/main.yml, sorry.
  * parse_switchmap
    * Gather switch data from netbox to configure a switch
  * netbox_add_vm
    * Create a new VM in netbox
