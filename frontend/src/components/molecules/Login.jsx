import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login({ setUserLoggedIn }) {
  const [text, setText] = useState("Please Login to continue");
  const containerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!containerRef.current || containerRef.current.querySelector('script')) return;

    window.TelegramLoginWidget = {
      dataOnauth: (user) => {
        if (user.username === "lakshaynz") {
          setUserLoggedIn(true);
          navigate('/');
        } else {
          setText("Unauthorized, Please contact Lakshay");
        }
      }
    };
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', 'dash_lak_nz_bot');
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)');
    script.setAttribute('data-request-access', 'write');
    script.async = true;
    containerRef.current.appendChild(script);
  }, [setUserLoggedIn, navigate]);

  return (
    <div>
      <p>{text}</p>
      <div ref={containerRef}></div>
    </div>
  );
}

export default Login;
