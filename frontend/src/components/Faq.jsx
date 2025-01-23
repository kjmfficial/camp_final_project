import React, { useEffect, useState } from "react";
import axios from "axios";

const FAQ = () => {
  const [faqs, setFaqs] = useState([]); // FAQ 데이터 상태
  const [error, setError] = useState(""); // 에러 메시지 상태
  const [isLoading, setIsLoading] = useState(true); // 로딩 상태
  const [searchTerm, setSearchTerm] = useState(""); // 검색 상태
  const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;

  useEffect(() => {
    // FAQ 데이터를 가져오는 함수
    const fetchFAQs = async () => {
      try {
        const response = await axios.get(`http://${API_URL}/api/faq`);
        setFaqs(response.data.terms.map((faq) => ({ ...faq, isOpen: false }))); // 초기 isOpen: false
      } catch (err) {
        setError("FAQ 데이터를 불러오는 데 실패했습니다.");
      } finally {
        setIsLoading(false); // 로딩 종료
      }
    };

    fetchFAQs();
  }, []);

  // 클릭 시 답변을 토글하는 함수
  const toggleAnswer = (filteredIndex) => {
    // 원본 `faqs` 배열에서의 index를 계산
    const originalIndex = faqs.findIndex(
      (faq) => faq[0] === filteredFaqs[filteredIndex][0]
    );
  
    // `faqs` 상태를 업데이트
    setFaqs((prevFaqs) =>
      prevFaqs.map((faq, i) =>
        i === originalIndex ? { ...faq, isOpen: !faq.isOpen } : faq
      )
    );
  };

  // 검색 필터 적용
  const filteredFaqs = faqs.filter(
    (faq) =>
      faq[0].toLowerCase().includes(searchTerm.toLowerCase()) || // question
      faq[1].toLowerCase().includes(searchTerm.toLowerCase())    // answer
  );

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>FAQ</h1>

      {/* 검색 입력 필드 */}
      <div style={styles.searchContainer}>
        <input
          type="text"
          placeholder="검색어를 입력하세요..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={styles.searchInput}
        />
      </div>

      {isLoading ? (
        <p style={styles.loadingText}>로딩 중...</p>
      ) : error ? (
        <p style={styles.errorMessage}>{error}</p>
      ) : filteredFaqs.length > 0 ? (
        filteredFaqs.map((faq, index) => (
          <div key={index} style={styles.faqItem}>
            <div style={styles.question} onClick={() => toggleAnswer(index)}>
              Q: {faq[0]} {/* question */}
            </div>
            {faq.isOpen && (
              <div style={styles.answer}>
                A: {faq[1]} {/* answer */}
              </div>
            )}
          </div>
        ))
      ) : (
        <p style={styles.noResults}>검색 결과가 없습니다.</p>
      )}
    </div>
  );
};

// 스타일링 객체
const styles = {
  container: {
    margin: "20px auto",
    padding: "20px",
    maxWidth: "800px",
    backgroundColor: "#f9f9f9",
    borderRadius: "8px",
    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
    fontFamily: "'Roboto', sans-serif",
  },
  header: {
    textAlign: "center",
    color: "#57b6fe",
    fontSize: "2.5rem",
    marginBottom: "20px",
  },
  searchContainer: {
    textAlign: "center",
    marginBottom: "20px",
  },
  searchInput: {
    padding: "10px",
    width: "90%",
    maxWidth: "600px",
    borderRadius: "5px",
    border: '1px solid #57b6fe',
    fontSize: "1rem",
  },
  loadingText: {
    textAlign: "center",
    fontSize: "1.2rem",
    color: "#777",
  },
  errorMessage: {
    textAlign: "center",
    fontSize: "1.2rem",
    color: "red",
  },
  faqItem: {
    borderBottom: "1px solid #ddd",
    padding: "15px 0",
    marginBottom: "10px",
  },
  question: {
    color: "#333",
    fontSize: "1.2rem",
    cursor: "pointer",
    transition: "color 0.3s ease",
  },
  answer: {
    color: "#555",
    fontSize: "1rem",
    marginTop: "10px",
    paddingLeft: "15px",
  },
  noResults: {
    textAlign: "center",
    fontSize: "1.2rem",
    color: "#777",
  },
};

// Hover 효과 추가
styles.question[":hover"] = {
  color: "#57b6fe",
};

export default FAQ;
