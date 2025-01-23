import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { UserContext } from "./UserContext.jsx";
import axios from "axios";  // axios를 사용한다고 가정

const Navbar = () => {

  const { user } = useContext(UserContext);

  const handleLogout = async () => {
    const token = localStorage.getItem("access_token");
    if (token) {
      try {
        await axios.post(`http://${API_URL}/api/logout`, {}, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error("Failed to log out from the server:", error);
      }
    }

    // 토큰 삭제 및 페이지 리디렉션
    localStorage.removeItem("access_token");
    window.location.href = "/";
  };

  return (
    <nav style={{zIndex:10}}className="navbar navbar-expand-lg navbar-light bg-light">
      <div className="container-fluid">
        <a className="navbar-brand" href="/">홈</a>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav">
            <li className="nav-item">
              <Link to="/term" style={{ fontSize: "1.2rem" }} className="nav-link">용어</Link>
            </li>
            <li className="nav-item">
              <Link to="/calendar" style={{ fontSize: "1.2rem" }} className="nav-link">청약캘린더</Link>
            </li>
            <li className="nav-item">
              <Link to="/analysis" style={{ fontSize: "1.2rem" }} className="nav-link">경쟁률 분석</Link>
            </li>
            <li className="nav-item">
              <Link to="/faq" style={{ fontSize: "1.2rem" }} className="nav-link">FAQ</Link>
            </li>
            <li className="nav-item">
              <Link to="/myInfo" style={{ fontSize: "1.2rem" }} className="nav-link">내정보</Link>
            </li>
          </ul>
          {/* 로그인/로그아웃 버튼을 오른쪽 끝에 배치 */}
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              {user ? (
                <>
                  <Link 
                    to="/login" 
                    className="nav-link"
                    onClick={async (e) => {
                      e.preventDefault(); // Link 기본 동작 방지
                      await handleLogout(); // 로그아웃 처리
                      window.location.href = "/login"; // 로그인 페이지로 리다이렉트
                    }}
                    style={{ fontSize: "1.2rem" }}
                  >
                    로그아웃
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/login" style={{ fontSize: "1.2rem" }} className="nav-link">
                    로그인
                  </Link>
                </>
              )}
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
