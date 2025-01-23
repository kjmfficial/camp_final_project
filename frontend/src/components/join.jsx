import React, { useState } from "react";
import axios from "axios";

function Join() {
  const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;
  const [formData, setFormData] = useState({
    id: "",
    password: "",
    confirmPassword: "",
    name: "",
    residentNumber: "",
    email: "",
    phoneNumber: "",
    address: "",
    bankbook: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const response = await axios.post(
        `http://${API_URL}/api/join`,
        new URLSearchParams({
          id: formData.id,
          password: formData.password,
          confirm_password: formData.confirmPassword,
          name: formData.name,
          resident_number: formData.residentNumber,
          email: formData.email,
          phone_number: formData.phoneNumber,
          address: formData.address,
          bankbook: formData.bankbook,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );

      if (response.data.error) {
        setError(response.data.error);
      } else {
        alert("회원가입이 완료되었습니다.");
        setFormData({
          id: "",
          password: "",
          confirmPassword: "",
          name: "",
          residentNumber: "",
          email: "",
          phoneNumber: "",
          address: "",
          bankbook: "",
        });
        window.location.href = "/login";
        setError("");
      }
    } catch (err) {
      console.error(err);
      setError("회원가입에 실패했습니다. 다시 시도해주세요.");
    }
  };

  return (
    <div style={styles.centeredContainer}>
      <div className="join-container" style={styles.formContainer}>
        <h2 style={styles.formTitle}>회원가입</h2>
        {error && <p style={styles.errorMessage}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>아이디</label>
            <input
              type="text"
              name="id"
              value={formData.id}
              onChange={handleChange}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>비밀번호</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              minLength={8}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>비밀번호 확인</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>이름</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>생년월일 (YYMMDD)</label>
            <input
              type="text"
              name="residentNumber"
              value={formData.residentNumber}
              onChange={handleChange}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>이메일</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>전화번호</label>
            <input
              type="text"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>주소</label>
            <select
            name="address"
            value={formData.address}
            onChange={handleChange}
            required
            style={{ ...styles.input, fontFamily: "'Arial', sans-serif" }} // 폰트 기본값으로 설정
          >
            <option value="" disabled>
              지역 선택
            </option>
            {[
              "강원",
              "경기",
              "경남",
              "경북",
              "광주",
              "대구",
              "대전",
              "부산",
              "서울",
              "세종",
              "울산",
              "인천",
              "전남",
              "전북",
              "제주",
              "충남",
            ].map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>통장 유무</label>
            <div style={styles.radioGroup}>
              <label>
                <input
                  type="radio"
                  name="bankbook"
                  value="yes"
                  checked={formData.bankbook === "yes"}
                  onChange={handleChange}
                  required
                  style={styles.radioInput}
                />{" "}
                예
              </label>
              <label>
                <input
                  type="radio"
                  name="bankbook"
                  value="no"
                  checked={formData.bankbook === "no"}
                  onChange={handleChange}
                  required
                  style={styles.radioInput}
                />{" "}
                아니오
              </label>
            </div>
          </div>
          <div>
            <button type="submit" style={styles.submitButton}>가입하기</button>
          </div>
        </form>
      </div>
    </div>
  );
}

// 스타일 정의
const styles = {
  centeredContainer: {
    display: "flex",
    justifyContent: "center", // 가로 중앙 정렬
    alignItems: "center", // 세로 중앙 정렬
    height: "100vh", // 화면 전체 높이
    background: "linear-gradient(#f0f7ff, #e0efff)", // 배경색
    
  },
  formContainer: {
    backgroundColor: "#fff",
    padding: "30px",
    borderRadius: "10px",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    minWidth: "300px", // 최소 너비 설정
    maxWidth: "400px", // 최대 너비 설정
    width: "100%",
  },
  formTitle: {
    textAlign: "center",
    marginBottom: "20px",
    fontSize: "24px",
    color: "#333",
  },
  errorMessage: {
    color: "red",
    fontSize: "14px",
    marginBottom: "15px",
  },
  inputGroup: {
    marginBottom: "15px",
  },
  label: {
    display: "block",
    marginBottom: "5px",
    fontSize: "14px",
    color: "#555",
  },
  input: {
    width: "100%",
    padding: "10px",
    fontSize: "14px",
    borderRadius: "5px",
    border: "1px solid #ddd",
    boxSizing: "border-box",
  },
  radioGroup: {
    display: "flex",
    gap: "10px",
  },
  radioInput: {
    marginRight: "5px",
  },
  submitButton: {
    width: "100%",
    padding: "10px",
    backgroundColor: "#57b6fe",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    fontSize: "16px",
    cursor: "pointer",
    transition: "background-color 0.3s",
  },
};

export default Join;
