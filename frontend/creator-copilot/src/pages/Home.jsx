import { useState } from "react";
import axios from "axios";

function Home() {
  const [message, setMessage] = useState("");

  const connectBackend = async () => {
    try {
      const response = await axios.get(
        "http://localhost:5000/test"
      );

      setMessage(response.data.message);
    } catch (error) {
      console.error(error);
      setMessage("Connection Failed");
    }
  };

  return (
    <div>
      <h1>Instagram Creator Co-Pilot</h1>

      <button onClick={connectBackend}>
        Connect Backend
      </button>

      <h3>{message}</h3>
    </div>
  );
}

export default Home;