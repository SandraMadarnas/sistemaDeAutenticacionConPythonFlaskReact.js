import React from "react";

import { useNavigate } from "react-router-dom";

import useAppContext from "../store/AppContext.js";

const Register = () => {

  const {store, actions} = useAppContext();

  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();

    actions.handleSubmitRegister(e);

    navigate("/login")

  }



  return (
    <form className="container">
      <h2>REGISTRO DEL USUARIO:</h2>
      <div className="mb-3">
        <label htmlFor="exampleInputEmail1" className="form-label">
          Email address
        </label>
        <input
          type="email"
          className="form-control"
          id="exampleInputEmail1"
          aria-describedby="emailHelp"
          placeholder="Introduzca el nuevo email"
          value={store.email}
          onChange={(e) => actions.setEmail(e.target.value)}
        />
        <div id="emailHelp" className="form-text fs-6 fst-italic">
          We'll never share your email with anyone else.
        </div>
      </div>
      <div className="mb-3">
        <label htmlFor="exampleInputPassword1" className="form-label">
          Password
        </label>
        <input
          type="password"
          className="form-control"
          id="exampleInputPassword1"
          placeholder="Introduzca la nueva contraseña"
          value={store.password}
          onChange={(e) => actions.setPassword(e.target.value)}
        />
      </div>
      <button type="submit" className="btn btn-primary" onClick={(e) => handleSubmit(e)}>
        Submit
      </button>
    </form>
  );
};

export default Register;
