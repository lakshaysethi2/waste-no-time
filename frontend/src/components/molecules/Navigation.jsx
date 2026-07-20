import { Link } from 'react-router-dom';
import "./buttonStyle.css"

function toggleFullScreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else if (document.exitFullscreen) {
    document.exitFullscreen();
  }
}

function Navigation({userLoggedIn,getData}) {
  return (
    <div>
      {userLoggedIn && <Link className="button-style" to="/">Home</Link>}
      {userLoggedIn && <Link className="button-style" to="/going">Trajectory</Link>}
      {userLoggedIn && <Link className="button-style" to="/RLNS">RLNS</Link>}
      {userLoggedIn && <Link className="button-style" to="/WRK">WRK</Link>}
      {userLoggedIn && <Link className="button-style" to="/RMB">RMB</Link>}
      {userLoggedIn && <Link className="button-style" to="/HLTH">HLTH</Link>}
      {userLoggedIn && <Link className="button-style" to="/top/24">Last 24 hours</Link>}
      {userLoggedIn && <Link className="button-style" to="/top/48">Last 48 hours</Link>}
      {userLoggedIn && <Link className="button-style" to="/top/72">Last 72 hours</Link>}
      {userLoggedIn && <Link className="button-style" to="/top/120">Last 5 days </Link>}
      {userLoggedIn && <Link className="button-style" to="/top/168">Last 168 hrs</Link>}
      {userLoggedIn && <Link className="button-style" to="/top/336">Last 336 hrs</Link>}
      {userLoggedIn && <Link className="button-style" to="/top/720">Last 720 hrs</Link>}
      <Link className="button-style" to="/top/2160">Last 2160 hrs</Link>
      <Link  className="button-style" onClick={ ()=>toggleFullScreen()} > FullScreen  </Link>
      {!userLoggedIn && <Link className="button-style" to="/login">Login</Link>}
      {userLoggedIn && <div onClick={()=>getData()} className="button-style" > Get New Data </div>}
    </div>
  );
}

export default Navigation
