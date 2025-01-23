import React, { useEffect, useState } from "react";
import axios from "axios";

const Terms = () => {
  const [terms, setTerms] = useState([]);
  const [filteredTerms, setFilteredTerms] = useState([]); // 추가된 상태
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState(""); // 검색어 상태 추가
  const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;

  // API 호출 (기존 코드 유지)
  useEffect(() => {
    const fetchTerms = async () => {
      try {
        const response = await axios.get(`http://${API_URL}/api/term`);
        setTerms(response.data.terms);
        setFilteredTerms(response.data.terms); // 초기 필터링 데이터도 설정
      } catch (err) {
        setError("데이터를 가져오는 중 오류가 발생했습니다.");
      }
    };

    fetchTerms();
  }, []);

  // 검색 로직 추가
  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchTerm(value);

    // 대소문자 구분 없이 검색
    const filtered = terms.filter(([term]) => 
      term.toLowerCase().includes(value.toLowerCase())
    );

    setFilteredTerms(filtered);
  };

  return (
    <div style={styles.container}>
      <div style={styles.searchContainer}>
        <input
          type="text"
          placeholder="용어 검색"
          value={searchTerm}
          onChange={handleSearch}
          style={styles.searchInput}
        />
      </div>
 
      <h1 style={styles.header}>용어 설명</h1>
      {error && <p style={styles.errorMessage}>{error}</p>}
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={{ ...styles.tableHeader, width: "20%" }}>용어</th>
            <th style={{ ...styles.tableHeader, width: "80%" }}>개념</th>
          </tr>
        </thead>
        <tbody>
          {filteredTerms.length > 0 ? (
            filteredTerms.map(([term, definition], index) => (
              <tr key={index}>
                <td style={styles.tableCell}>{term}</td>
                <td style={styles.tableCell}>{definition}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="2" style={styles.loadingCell}>
                {searchTerm ? "검색 결과가 없습니다." : "용어 데이터를 불러오는 중입니다..."}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};


// 스타일링 객체
const styles = {
  container: {
    margin: "30px auto",
    padding: "20px",
    maxWidth: "900px",
    backgroundColor: "#ffffff",
    borderRadius: "10px",
    boxShadow: "0 6px 15px rgba(0, 0, 0, 0.15)",
    fontFamily: "'Roboto', sans-serif",
  },
  header: {
    textAlign: "center",
    color: "#2c3e50",
    fontSize: "2.5rem",
    marginBottom: "20px",
    borderBottom: "2px solid #57b6fe",
    paddingBottom: "10px",
  },
  errorMessage: {
    color: "#e74c3c",
    textAlign: "center",
    fontSize: "1.2rem",
    marginBottom: "20px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "20px",
    overflow: "hidden",
  },
  tableHeader: {
    padding: "14px",
    backgroundColor: "#57b6fe",
    color: "white",
    textAlign: "left",
    fontSize: "1.2rem",
    fontWeight: "bold",
  },
  tableCell: {
    padding: "12px",
    border: "1px solid #ddd",
    textAlign: "left",
    fontSize: "1rem",
    backgroundColor: "#f9f9f9",
    transition: "background-color 0.3s ease",
  },
  loadingCell: {
    padding: "12px",
    border: "1px solid #ddd",
    textAlign: "center",
    fontSize: "1rem",
    backgroundColor: "#f0f0f0",
  },
  // 테이블 Hover 효과 추가
  tableRowHover: {
    ":hover": {
      backgroundColor: "#e3f2fd",
    },
  },
  searchContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginBottom: '20px'
  },
  searchInput : {
    padding: '10px',
    width: '250px',
    borderRadius: '5px',
    border: '1px solid #57b6fe', // 기본 테두리 색상 변경
    fontSize: '1rem',
    outline: 'none',
    transition: 'border-color 0.3s ease',
  }

};

export default Terms;
