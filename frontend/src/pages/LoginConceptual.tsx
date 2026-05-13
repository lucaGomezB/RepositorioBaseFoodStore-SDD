import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login({ onLogin }: { onLogin: (role: 'admin' | 'guest') => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Obtener credenciales del .env
    const envUser = import.meta.env.VITE_LOGIN_USER;
    const envPass = import.meta.env.VITE_LOGIN_PASS;

    if (username === envUser && password === envPass) {
      localStorage.setItem("userRole", "admin");
      onLogin('admin');
      navigate("/");
    } else {
      setError("Credenciales incorrectas");
    }
  };

  const handleGuestLogin = () => {
    localStorage.setItem("userRole", "guest");
    onLogin('guest');
    navigate("/productos");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6 text-center text-gray-800">
          Iniciar Sesión
        </h1>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Usuario
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 px-3 py-2 rounded focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 px-3 py-2 rounded focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-2 transition-colors cursor-pointer"
          >
            Entrar
          </button>
        </form>

        <div className="mt-6 text-center">
          <div className="relative mb-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">O ingresa como invitado</span>
            </div>
          </div>
          <button
            onClick={handleGuestLogin}
            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-4 border border-gray-300 rounded transition-colors cursor-pointer"
          >
            Ver Menú (Invitado)
          </button>
        </div>
      </div>
    </div>
  );
}
