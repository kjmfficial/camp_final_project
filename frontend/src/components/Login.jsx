import React, { useState } from "react";
import axios from "axios"; // Axios import
import { Link } from 'react-router-dom';


const Login = () => {
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;
  
  const handleLogin = async (e) => {
    e.preventDefault();
    setError(""); // 에러 메시지 초기화
    setIsLoading(true);

    const formData = new FormData();
    formData.append("id", id);
    formData.append("password", password);

    try {
      const response = await axios.post(`http://${API_URL}/api/login`, formData, {
        headers: {
          "Content-Type": "multipart/form-data", // FormData를 보내는 경우 설정
        },
      });
    
      if (response.data.access_token) {
        const token = response.data.access_token;
        localStorage.setItem("access_token", token); // 로컬 스토리지에 저장
        window.location.href = "/"; // 로그인 성공 후 페이지 이동
      } else if (response.data.error) {
        setError(response.data.error); // 서버에서 반환된 에러 메시지
      }
    } catch (err) {
      setError(
        err.response?.data?.error ||
        "An unexpected error occurred. Please try again later." // 일반 오류 메시지
      );
    } finally {
      setIsLoading(false); // 로딩 상태 종료
    }};

    return (
      <div style={styles.centeredContainer}>
        <div className="login-container" style={styles.formContainer}>
          <form onSubmit={handleLogin}>
            <table style={styles.table}>
              <tbody>
                <tr>
                  <td>
                    <h2 style={styles.header}>로그인</h2>
                  </td>
                </tr>
                <tr>
                  <td>
                    <input
                      type="text"
                      placeholder="ID"
                      name="id"
                      value={id}
                      onChange={(e) => setId(e.target.value)}
                      required
                      style={styles.input}
                    />
                  </td>
                </tr>
                <tr>
                  <td>
                    <input
                      type="password"
                      placeholder="Password"
                      name="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      minLength={8}
                      className="login-input"
                      style={styles.input}
                    />
                  </td>
                </tr>
                <tr>
                  <td>
                    <label style={styles.checkboxLabel}>
                      <input type="checkbox" style={styles.checkbox} /> 로그인 정보 저장
                    </label>
                  </td>
                </tr>
                {error && (
                  <tr>
                    <td>
                      <p style={styles.errorText}>{error}</p>
                    </td>
                  </tr>
                )}
                <tr>
                  <td>
                    <button type="submit" className="btn" disabled={isLoading} style={styles.button}>
                      {isLoading ? "Loading..." : "Sign in"}
                    </button>
                  </td>
                </tr>
                <tr>
                  <td className="link-container" style={styles.linkContainer}>
                    <div style={styles.linkWrapper}>
                      <Link to="/join" className="btn btn-primary" style={styles.link}>
                        회원가입
                      </Link>
                    </div>
                    <div style={styles.linkWrapper}>
                      <Link to="/id_search" className="btn btn-primary" style={styles.link}>
                        아이디 찾기
                      </Link>
                    </div>
                    <div style={styles.linkWrapper}>
                      <Link to="/password_update" className="btn btn-primary" style={styles.link}>
                        비밀번호 재설정
                      </Link>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </form>
        </div>
      </div>
    );
  };


// 스타일 정의
const styles = {
  centeredContainer: {
    display: "flex",
    justifyContent: "center", // 가로 중앙 정렬
    alignItems: "center", // 세로 중앙 정렬
    height: "100vh", // 화면 전체 높이
  },
  formContainer: {
    backgroundColor: "#fff",
    padding: "30px", // 여백을 더 추가
    borderRadius: "12px", // 둥근 모서리
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)", // 더 부드러운 그림자
    minWidth: "320px", // 최소 너비
    maxWidth: "450px", // 최대 너비
    width: "100%",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse", // 테이블 간격 없애기
  },
  header: {
    textAlign: "center",
    fontSize: "28px",
    color: "#333",
    marginBottom: "20px",
    fontFamily: "'Roboto', sans-serif",
  },
  input: {
    width: "100%",
    padding: "12px 15px",
    fontSize: "16px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    marginBottom: "20px",
    boxSizing: "border-box",
    outline: "none",
    transition: "0.3s",
  },
  inputFocus: {
    borderColor: "#57b6fe", // Focus 시 색상 변경
  },
  checkboxLabel: {
    fontSize: "14px",
    color: "#666",
  },
  checkbox: {
    marginRight: "8px",
  },
  errorText: {
    color: "red",
    fontSize: "14px",
    textAlign: "center",
  },
  button: {
    width: "100%", // 버튼 너비를 100%로 설정
    padding: "12px 0", // 버튼 패딩을 동일하게 설정
    backgroundColor: "#57b6fe",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "16px",
    transition: "background-color 0.3s",
  },
  buttonDisabled: {
    backgroundColor: "#cccccc",
  },
  linkContainer: {
    display: "flex", // 가로 배치
    justifyContent: "space-between", // 버튼 간의 일정 간격
    gap: "10px", // 버튼 간의 간격
    padding: "10px 0", // 상하 여백 추가
  },
  linkWrapper: {
    display: "flex", // Flexbox 적용
    justifyContent: "center", // 수평 중앙 정렬
    alignItems: "center", // 수직 중앙 정렬
    width: "30%", // 각 버튼을 3등분하여 배치
  },
  link: {
    display: "inline-flex", // 텍스트를 세로로 중앙 정렬하기 위해 inline-flex 사용
    justifyContent: "center", // 수평 중앙 정렬
    alignItems: "center", // 수직 중앙 정렬
    width: "100%", // 부모의 너비에 맞게 100%로 설정
    padding: "12px 0", // 버튼 높이 맞추기
    backgroundColor: "#57b6fe",
    color: "#fff",
    borderRadius: "8px",
    textDecoration: "none",
    textAlign: "center",
    fontSize: "16px",
    transition: "background-color 0.3s",
  },
  linkHover: {
    backgroundColor: "#007bff",
  },
};


export default Login;
