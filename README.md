x-tenancy-migration.sh instructions

Add endorse policies to target
  Define tenancy SourceTenancy as <source tenancy OCID>
  Endorse group Administrators to read boot-volume-backups in tenancy SourceTenancy
  Endorse group Administrators to manage all-resources in tenancy SourceTenancy		
Add admit policies to source
  Define tenancy TargetTenancy as <target tenancy OCID>
 Define group TargetAdministrators as <target tenancy administrators group OCID>
 Admit group TargetAdministrators of tenancy TargetTenancy to read boot-volume-backups in Tenancy
 Admit group TargetAdministrators of tenancy TargetTenancy to manage all-resources in Tenancy	

Create a volume group for each availability domain (AD) where you have instances.
-	indicate AD in volume group name (i.e "VolumeGroup-AD1")
Add all boot and block volumes that should be migrated to the volume group in its AD. 
Verify all boot and block volumes are present in volume groups across all 3 ADs.
-	Click into each vg, check the "block volumes" and "boot volumes" tabs

Open the cloud shell in the OCI console.
Move the x-tenancy-migration.sh script and config.ini into a working directory.
Update the config.ini file with the appropriate values.
Shut down all source instances. 
For each volume group, run migration.sh script in the OCI console cloud shell.
-	Update VOLUMEGROUP in the config.ini file for subsequent volume groups  
After all volumes are moved over, spin up new instances with the boot volumes.
-	Set the private IP during this step
-	Reserved public IPs are recommended
Attach block volumes to the appropriate instances. 
Update DNS records to point to new public IPs.


Add backups to copy?
Copy NVICs?




