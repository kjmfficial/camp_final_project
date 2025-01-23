import React, { useState } from "react";
import axios from "axios";

function Analysis() {
  const [region, setRegion] = useState("");
  const [year, setYear] = useState("");
  const [home, setHome] = useState("");
  const [data, setData] = useState(null);
  const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const formData = new FormData();
      formData.append("region", region);
      formData.append("year", year);
      formData.append("home", home);

      const response = await axios.post(`http://${API_URL}/api/analysis`, formData);
      const { data } = response.data;

      setData(data);
    } catch (error) {
      console.error("Error during analysis:", error);
      alert("데이터를 불러오는 중 오류가 발생했습니다.");
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>지역 및 연도별 경쟁률 분석</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        {/* 지역 선택 */}
        <div style={styles.inputGroup}>
          <label htmlFor="region" style={styles.label}>지역 선택</label>
          <select
            id="region"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            style={{ ...styles.select, fontFamily: "'Arial', sans-serif" }}
            required
          >
            <option value="" disabled>지역 선택</option>
            <option value="강원">강원</option>
            <option value="경기">경기</option>
            <option value="경남">경남</option>
            <option value="경북">경북</option>
            <option value="광주">광주</option>
            <option value="대구">대구</option>
            <option value="대전">대전</option>
            <option value="부산">부산</option>
            <option value="서울">서울</option>
            <option value="세종">세종</option>
            <option value="울산">울산</option>
            <option value="인천">인천</option>
            <option value="전남">전남</option>
            <option value="전북">전북</option>
            <option value="제주">제주</option>
            <option value="충남">충남</option>
          </select>
        </div>

        {/* 년도 선택 */}
        <div style={styles.inputGroup}>
          <label htmlFor="year" style={styles.label}>년도 선택</label>
          <select
            id="year"
            value={year}
            style={{ ...styles.select, fontFamily: "'Arial', sans-serif" }}
            onChange={(e) => setYear(e.target.value)}
            required
          >
            <option value="" disabled>년도 선택</option>
            <option value="2020">2020</option>
            <option value="2021">2021</option>
            <option value="2022">2022</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
          </select>
        </div>

        {/* 청약 선택 */}
        <div style={styles.inputGroup}>
          <label htmlFor="home" style={styles.label}>청약 선택</label>
          <select
            id="home"
            value={home}
            style={{ ...styles.select, fontFamily: "'Arial', sans-serif" }}
            onChange={(e) => setHome(e.target.value)}
            required
          >
            <option value="" disabled>청약 선택</option>
            <option value="general">일반 공급</option>
            <option value="special">특별 공급</option>
          </select>
        </div>

        <button type="submit" style={styles.button}>분석</button>
      </form>

      {/* 데이터 결과 */}
      {data && (
        <div style={styles.resultContainer}>
          <h2 style={styles.resultHeading}>결과 데이터</h2>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.tableHeader}>월</th>
                <th style={styles.tableHeader}>경쟁률</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index} style={styles.tableRow}>
                  <td style={styles.tableCell}>{item["month(`year_month`)"]}월</td>
                  {/* home 값에 따라 출력할 데이터 변경 */}
                  <td style={styles.tableCell}>
                    {home === "general"
                      ? item["general_supply_competition_rate"]
                      : item["special_supply_competition_rate"]}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "800px",
    margin: "20px auto",
    padding: "20px",
    backgroundColor: "#fdfdfd",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    borderRadius: "12px",
  },
  heading: {
    textAlign: "center",
    color: "#333",
    marginBottom: "20px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  inputGroup: {
    display: "flex",
    flexDirection: "column",
  },
  label: {
    marginBottom: "8px",
    fontWeight: "bold",
    color: "#555",
  },
  select: {
    width: "100%",
    padding: "12px 15px",
    fontSize: "16px",
    color: "#333",
    backgroundColor: "#f9f9f9",
    border: "1px solid #ddd",
    borderRadius: "8px",
    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
  },
  button: {
    padding: "12px 20px",
    fontSize: "16px",
    fontWeight: "bold",
    color: "#fff",
    backgroundColor: "#57b6fe",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
  resultContainer: {
    marginTop: "30px",
    padding: "20px",
    backgroundColor: "#f5f5f5",
    borderRadius: "8px",
    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
  },
  resultHeading: {
    color: "#333",
    marginBottom: "15px",
    textAlign: "center",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "10px",
  },
  tableHeader: {
    borderBottom: "2px solid #ddd",
    padding: "10px",
    fontWeight: "bold",
    textAlign: "left",
  },
  tableRow: {
    borderBottom: "1px solid #eee",
  },
  tableCell: {
    padding: "10px",
    textAlign: "left",
  },
};

export default Analysis;
