
export const login = async (email, pass) => {
    const resp = await fetch(
        `https://3001-giousned-proyectauthent-x2436g3b4hv.ws-eu96b.gitpod.io/token`,
        {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, pass }),
        }
    );

    if (!resp.ok) throw Error("There was a problem in the login request");

    if (resp.status === 401) {
        throw "Invalid credentials";
    } else if (resp.status === 400) {
        throw "Invalid email or password format";
    }

    const data = await resp.json();

    // save your token in the sessionStorage
    // also you should set your user into the store using the setStore function

    sessionStorage.setItem("jwt-token", data.token);        // cookies. .... CASI MEJOR, PERO CASI NUNCA USAR LOCALSTORAGE QUIZAS EN TIENDAS...

    return data;
  };

export const register = async (email, pass) => {
    const resp = await fetch(
        `https://3001-giousned-proyectauthent-x2436g3b4hv.ws-eu96b.gitpod.io/signup`,
        {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, pass }),
        }
    );

    if (!resp.ok) throw Error("There was a problem in the login request");

    if (resp.status === 401) {
        throw "Invalid credentials";
    } else if (resp.status === 400) {
        throw "Invalid email or password format";
    }

    const data = await resp.json();

    return data;
  };


// asumiendo que "/protected" es un endpoint privado
export const getMyToken = async () => {
    // retrieve token form sessionStorage
    const token = sessionStorage.getItem("jwt-token");

    const resp = await fetch(
        `https://3001-giousned-proyectauthent-x2436g3b4hv.ws-eu96b.gitpod.io/protected`,
        {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token // ⬅⬅⬅ authorization token
        }
        }
    );

    if (!resp.ok) throw Error("There was a problem in the login request");

    if (resp.status === 403) {
        throw "Missing or invalid token";
    }
    else if (resp.status === 500) throw "Unknown error";

    const data = await resp.json();

    console.log("This is the data you requested", data);

    return data;
};