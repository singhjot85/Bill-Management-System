async function makeApiCall(url, method = "GET", data = null) {
  try {
    const options = {
      method: method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    if (data && method !== "GET") {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);

    let responseData = {};
    try {
      responseData = await response.json();
    } catch {
      responseData = {};
    }
    if (!response.ok) {
      throw new Error(
        responseData.message ||
          responseData.detail ||
          `Request failed (${response.status})`,
      );
    }

    return {
      status: response.status,
      response: responseData,
      ok: true,
    };
  } catch (error) {
    showSnackbar(error.message || "Unexpected API error");
    return {
      status: 500,
      response: null,
      ok: false,
    };
  }
}

window.logoutUser = async function logoutUser() {
  await makeApiCall("logout/", "GET");
  window.location.href = "/";
}
