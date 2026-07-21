import { useState } from 'react';
import axios from 'axios';
import TelegramLoginButton from 'react-telegram-login';

function Login({ setAuthData, setUserLoggedIn }) {
  const [text, setText] = useState('Please log in to continue');

  const handleTelegramResponse = async (response) => {
    try {
      // Telegram's browser callback is not trusted until Django verifies its hash.
      const result = await axios.post('/api/auth/telegram', response);
      setAuthData(result.data);
      setUserLoggedIn(true);
    } catch {
      setText('Login could not be verified. Please try again.');
    }
  };

  const botName = import.meta.env.VITE_TELEGRAM_BOT_USERNAME;
  if (!botName) {
    return <p>Dashboard login is not configured.</p>;
  }

  return (
    <div>
      <p>{text}</p>
      <TelegramLoginButton dataOnauth={handleTelegramResponse} botName={botName} />
    </div>
  );
}

export default Login;
