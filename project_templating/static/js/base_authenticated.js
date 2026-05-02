// import { makeapiCall } from './base';

async function openDjangoAdmin() {
  try {
    const response = await makeApiCall("/has_perm", {
      permissions_to_check: ["is_staff", "is_superuser"],
    });

    if (
      response?.ok &&
      response?.response &&
      Object.values(response.response).every(Boolean)
    ) {
      window.location.href = "/admin";
    } else {
      showSnackbar("Insufficient access for Admin");
    }
  } catch (error) {
    console.error("Permission check failed:", error);
    showSnackbar("Something went wrong. Please try again.");
  }
}
