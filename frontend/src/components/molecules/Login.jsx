import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login({ setAuthData, setUserLoggedIn }) {
  const [text, setText] = useState('Please log in to continue');
  const containerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!containerRef.current || containerRef.current.querySelector('script')) return;

    window.TelegramLoginWidget = {
      dataOnauth: async (user) => {
        try {
          // Server-side HMAC verification
          const result = await axios.post('/api/auth/telegram', user);
          setAuthData(result.data);
          setUserLoggedIn(true);
          navigate('/');
        } catch {
          setText('Login could not be verified. Please try again.');
        }
      }
    };

    const botName = import.meta.env.VITE_TELEGRAM_BOT_USERNAME;
    if (!botName) {
      setText('Dashboard login is not configured.');
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botName);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)');
    script.setAttribute('data-request-access', 'write');
    script.async = true;
    containerRef.current.appendChild(script);
  }, [setAuthData, setUserLoggedIn, navigate]);

  return (
    <div>
      <p>{text}</p>
      <div ref={containerRef}></div>
    </div>
  );
}

export default Login;
