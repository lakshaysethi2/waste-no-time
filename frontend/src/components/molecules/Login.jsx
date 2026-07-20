import React , { useState } from 'react';
import TelegramLoginButton from 'react-telegram-login';

function Login({setUserLoggedIn} ) {
  const [text,setText] = useState("Please Login to continue")
  const handleTelegramResponse = response => {
    if (response.username === "lakshaynz"){
      setUserLoggedIn(true)
    }else{
      setText("Unauthorized, Please contact Lakshay")
    }
  };
 
  return (
    <div>
      <p>{text}</p>
      <TelegramLoginButton 
        dataOnauth={handleTelegramResponse} 
        botName="dash_lak_nz_bot" 
      />
    </div>
  )
}

export default Login
 
