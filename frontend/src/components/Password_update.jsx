import React, { useState } from "react";
import axios from "axios";

const PasswordUpdate = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("id", id);
    formData.append("password", password);

    try {
      const response = await axios.put(
        `http://${API_URL}/api/password_update`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setMessage(response.data.complete || "");
      setError("");
    } catch (err) {
      if (err.response) {
        setMessage("");
        setError(
          err.response.data.error || "입력된 정보가 정확하지 않습니다. 입력 정보를 확인해주세요."
        );
      } else {
        setMessage("");
        setError("서버에 연결할 수 없습니다. 나중에 다시 시도해주세요.");
      }
    }
  };

  return (
    <div style={styles.centeredContainer}>
      <div style={styles.formContainer}>
        <h2>비밀번호 재설정</h2>
        <form onSubmit={handleSubmit}>
          <div style={styles.inputGroup}>
            <label>이름</label>
            <input
              type="text"
              placeholder="이름"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={styles.input}
              required
            />
          </div>
          <div style={styles.inputGroup}>
            <label>ID</label>
            <input
              type="text"
              placeholder="ID"
              value={id}
              onChange={(e) => setId(e.target.value)}
              style={styles.input}
              required
            />
          </div>
          <div style={styles.inputGroup}>
            <label>이메일</label>
            <input
              type="email"
              placeholder="이메일"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              required
            />
          </div>
          <div style={styles.inputGroup}>
            <label>새 비밀번호</label>
            <input
              type="password"
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              required
            />
          </div>
          <div style={styles.submitButtonContainer}>
            <input
              type="submit"
              value="비밀번호 변경"
              className="btn"
              style={styles.submitButton}
            />
          </div>
        </form>

        {message && <p style={styles.resultText}>{message}</p>}
        {error && <p style={styles.errorText}>{error}</p>}

        <a href="/login" style={styles.backLink}>
          뒤로가기
        </a>
      </div>
    </div>
  );
};

const styles = {
  centeredContainer: {
    display: "flex",
    justifyContent: "center", // 가로 중앙 정렬
    alignItems: "center", // 세로 중앙 정렬
    height: "100vh", // 화면 전체 높이
    background: "linear-gradient(#f0f7ff, #e0efff)", // 그라디언트 배경색
  },
  formContainer: {
    backgroundColor: "#fff", // 흰색 배경
    padding: "20px",
    borderRadius: "10px",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    minWidth: "300px", // 최소 너비 설정
    maxWidth: "400px", // 최대 너비 설정
    width: "100%",
  },
  inputGroup: {
    marginBottom: "15px", // 각 입력 필드의 하단 여백
  },
  input: {
    width: "100%",
    padding: "10px",
    marginTop: "5px",
    borderRadius: "5px",
    border: "1px solid #ccc",
  },
  submitButtonContainer: {
    textAlign: "center", // 버튼 중앙 정렬
  },
  submitButton: {
    padding: "10px 20px",
    backgroundColor: "#57b6fe", // 버튼 배경색
    color: "white", // 글자 색
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    width: "100%", // 버튼 너비를 입력 필드와 동일하게 설정
  },
  resultText: {
    textAlign: "center",
    color: "#57b6fe", // 결과 텍스트 색
    fontWeight: "bold",
  },
  errorText: {
    textAlign: "center",
    color: "red", // 에러 메시지 색
  },
  backLink: {
    display: "block",
    textAlign: "center",
    marginTop: "20px",
    color: "#007bff", // 링크 색상
    textDecoration: "none",
  },
};

export default PasswordUpdate;
