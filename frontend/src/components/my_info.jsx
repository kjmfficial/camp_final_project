import React, { useContext } from "react";
import { UserContext } from "./UserContext.jsx";

function MyInfo() {
  const { user } = useContext(UserContext);

  if (!user) {
    alert("로그인 정보가 없습니다. 로그인 페이지로 갑니다.");
    window.location.href = "/login";
  }

  return <UserInfoView user={user} />;
}

const UserInfoView = ({ user }) => (
  <div style={styles.container}>
    <h1 style={styles.header}>어서오세요, {user?.name || "사용자"}님</h1>
    <br />
    <div style={styles.section}>
      <h2 style={styles.subHeader}>기본 정보</h2>
      <p style={styles.infoText}>이름: {user?.name || "정보 없음"}</p>
      <p style={styles.infoText}>생년월일: {user?.resident_number || "정보 없음"}</p>
      <p style={styles.infoText}>주소지: {user?.address || "정보 없음"}</p>
    </div>
    <br />
    <div style={styles.section}>
      <h2 style={styles.subHeader}>연락처 정보</h2>
      <p style={styles.infoText}>이메일: {user?.email || "정보 없음"}</p>
      <p style={styles.infoText}>휴대전화: {user?.phone_number || "정보 없음"}</p>
    </div>
  </div>
);

// 스타일 객체
const styles = {
  container: {
    margin: "20px auto",
    padding: "20px",
    maxWidth: "600px",
    backgroundColor: "#f9f9f9",
    borderRadius: "10px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
    fontFamily: "'Roboto', sans-serif",
  },
  header: {
    color: "#57b6fe",
    fontSize: "2rem",
    textAlign: "center",
    marginBottom: "10px",
  },
  section: {
    padding: "10px 0",
    borderBottom: "1px solid #ddd",
  },
  subHeader: {
    fontSize: "1.5rem",
    color: "#333",
    marginBottom: "8px",
  },
  infoText: {
    fontSize: "1.1rem",
    color: "#555",
    margin: "5px 0",
  },
};

export default MyInfo;
