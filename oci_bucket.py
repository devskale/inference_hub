# This is an automatically generated code sample.
# To make this code sample work in your Oracle Cloud tenancy,
# please replace the values for any parameters whose current values do not fit
# your use case (such as resource IDs, strings containing ‘EXAMPLE’ or ‘unique_id’, and
# boolean, number, and enum parameters with values not fitting your use case).

import oci

# Create a default config using DEFAULT profile in default location
# Refer to
# https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File
# for more info
config = oci.config.from_file( "./.oci/config", "DEFAULT")
#config = oci.config.from_file("~/.oci/config", "DEFAULT")

print(config)
exit()

# Initialize service client with default config file
object_storage_client = oci.object_storage.ObjectStorageClient(config)


# Send the request to service, some parameters are not required, see API
# doc for more info
list_buckets_response = object_storage_client.list_buckets(
    namespace_name="EXAMPLE-namespaceName-Value",
    compartment_id="ocid1.test.oc1..<unique_ID>EXAMPLE-compartmentId-Value",
    limit=602,
    page="EXAMPLE-page-Value",
    fields=["tags"],
    opc_client_request_id="ocid1.test.oc1..<unique_ID>EXAMPLE-opcClientRequestId-Value")

# Get the data from response
print(list_buckets_response.data)
