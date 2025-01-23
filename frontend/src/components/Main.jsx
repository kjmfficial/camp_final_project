import { useRef, useState, useEffect, useContext, createContext } from "react";
import { UserContext } from "./UserContext.jsx";
import { Link } from 'react-router-dom';

import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
// 
import Chatbot from './Chatbot';

const Main = () => {
  const { user } = useContext(UserContext);
  const [news, setNews] = useState([]);
  const [apt_upcoming_data, setAptUpcoming] = useState(null);
  const [unranked_upcoming_data, setUnrankedUpcoming] = useState(null);
  const [apt_grouped_data, setAptCompetition] = useState(null);
  const [unranked_grouped_data, setUnrankedCompetition] = useState(null);
  const API_URL = import.meta.env.VITE_EC2_PUBLIC_IP;
  const [isModalOpen, setIsModalOpen] = useState(false); // 모달 상태
  const [modalData, setModalData] = useState(null); // 모달에 표시할 데이터

  
  // API 호출 및 모달 열기
  const handleButtonClick = async (apartmentName) => {
    try {
      const response = await fetch(`http://${API_URL}/api/detail/${encodeURIComponent(apartmentName)}`);
      const data = await response.json();

      if (response.ok) {
        setModalData(data.grouped_data); // grouped_data가 리스트 형태여야 함
        setIsModalOpen(true);
      } else {
        alert(data.error || "정보를 불러오는 데 실패했습니다.");
      }
    } catch (error) {
      console.error("Error fetching competition data:", error);
      alert("오류가 발생했습니다. 다시 시도해주세요.");
    }
  };

  // 모달 닫기
  const closeModal = () => {
    setIsModalOpen(false);
    setModalData(null);
  };

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

  // Fetch news data
  useEffect(() => {
    axios
      .get(`http://${API_URL}/api/news`)
      .then((response) => {
        const { news } = response.data;
        setNews(news);
      })
      .catch((error) => console.error("데이터를 가져오는 중 오류 발생:", error));
  }, []);


  // Fetch news data
  useEffect(() => {
    axios
      .get(`http://${API_URL}/api/upcoming`)
      .then((response) => {
        const { apt_upcoming_data,unranked_upcoming_data } = response.data;
        setAptUpcoming(apt_upcoming_data);
        setUnrankedUpcoming(unranked_upcoming_data);
      })
      .catch((error) => console.error("데이터를 가져오는 중 오류 발생:", error));
  }, []);

  // Fetch user data
  useEffect(() => {
    axios
      .get(`http://${API_URL}/api/competition`)
      .then((response) => {
        const { apt_grouped_data,unranked_grouped_data } = response.data;
        setAptCompetition(apt_grouped_data);
        setUnrankedCompetition(unranked_grouped_data);
      })
      .catch((error) => console.error("데이터를 가져오는 중 오류 발생:", error));
  }, []);  

  return (
    <div>

   
<div
  className="d-flex flex-wrap justify-content-around"
  style={{
    maxWidth: "1600px",
    margin: "40px auto",
    gap: "10px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  }}
>
  <div
    id="newsCarousel"
    className="carousel slide"
    data-bs-ride="carousel"
    style={{ flex: 2, maxWidth: "1600px" }}
  >
    <h3>최신 청약 뉴스</h3>
    <div className="carousel-inner">
      {news.map((item, index) => (
        <div
          key={index}
          className={`carousel-item ${index === 0 ? "active" : ""}`}
        >
          <div
            className="card d-flex flex-column flex-lg-row align-items-center"
            style={{
              width: "100%",
              margin: "auto",
              padding: "20px",
              backgroundColor: "#f9f9f9",
              border: "1px solid #ddd",
              borderRadius: "10px",
            }}
          >
            {/* 이미지 섹션 */}
            <a
              href={item.link}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                flex: 1,
                textDecoration: "none",
                display: "block",
                maxWidth: "100%",
              }}
            >
              <img
                src={item.image}
                className="card-img-left"
                alt={item.title}
                style={{
                  width: "100%",
                  height: "auto",
                  objectFit: "cover",
                  borderRadius: "10px",
                }}
              />
            </a>

            {/* 텍스트 섹션 */}
            <div
              className="card-body"
              style={{
                flex: 2,
                textAlign: "center",
              }}
            >
              {/* 날짜 */}
              <p
                style={{
                  fontSize: "0.9rem",
                  color: "#888",
                  marginBottom: "5px",
                }}
              >
                {new Date(item.pubDate).toLocaleDateString("ko-KR", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </p>

              {/* 제목 */}
              <a
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
                className="card-title"
                style={{
                  fontWeight: "bold",
                  fontSize: "1.5rem",
                  textDecoration: "none",
                  color: "#57b6fe",
                }}
              >
                {item.tetle} {/* Note: Fix typo */}
              </a>

              {/* 설명 */}
              <p
                className="card-text"
                style={{
                  fontSize: "1rem",
                  color: "#555",
                  marginTop: "10px",
                }}
              >
                {item.description}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>

    {/* Carousel Controls */}
    <button
      className="carousel-control-prev"
      type="button"
      data-bs-target="#newsCarousel"
      data-bs-slide="prev"
      style={{
        position: "absolute",
        top: "130px",
        padding: "4px 6px",
        width: "40px",
        height: "40px",
        backgroundColor: "#57b6fe",
        color: "white",
        borderRadius: "50%",
        fontSize: "14px",
      }}
    >
      <span className="carousel-control-prev-icon" aria-hidden="true"></span>
      <span className="visually-hidden">Previous</span>
    </button>

    <button
      className="carousel-control-next"
      type="button"
      data-bs-target="#newsCarousel"
      data-bs-slide="next"
      style={{
        position: "absolute",
        top: "130px",
        padding: "4px 6px",
        width: "40px",
        height: "40px",
        backgroundColor: "#57b6fe",
        color: "white",
        borderRadius: "50%",
        fontSize: "14px",
      }}
    >
      <span className="carousel-control-next-icon" aria-hidden="true"></span>
      <span className="visually-hidden">Next</span>
    </button>
  </div>
</div>


<div 
  className="d-flex flex-wrap justify-content-start" // 'justify-content-center' -> 'justify-content-start'
  style={{ 
    maxWidth: "1600px", 
    margin: "40px auto", 
    gap: "0px", 
    display: "flex", 
    alignItems: "center",
  }}
>
  {/* 최신 경쟁률 제목 */}
  <h3 style={{ textAlign: "left"}}>최신 경쟁률</h3> {/* 텍스트 왼쪽 정렬 */}
  
  <div className="container" style={{ maxWidth: "750px", margin: "auto", border: "2px solid #57b6fe", borderRadius: "10px", padding: "15px", backgroundColor: "#f9f9f9" }}>
    <div className="d-flex justify-content-around flex-wrap" style={{ gap: "15px" }}>
      <div id="apt_competiton" className="carousel slide" data-bs-ride="carousel" style={{ maxWidth: "250" }}>
        <h4 style={{ textAlign: "center", marginBottom: "8px", fontWeight: "bold", color: "#6a75ca", fontSize: "1.2rem" }}>아파트</h4>
        <div className="carousel-inner">
          {apt_grouped_data && apt_grouped_data.map((group, index) => (
            <div key={index} className={`carousel-item ${index === 0 ? "active" : ""}`}>
              <div className="card" style={{ width: "14rem", margin: "auto" }}>
                <div className="card-body">
                  <a
                    style={{ textDecoration: "none", color: "inherit", fontSize: "1.2rem", fontWeight: "bold" }}
                  >
                    {group.apartment_name}
                  </a>
                  <br /><br />
                  <div><p style={{ fontSize: "0.9rem" }}>경쟁률: {group.total_competition_rate}</p></div>
                  <div><p style={{ fontSize: "0.9rem" }}>상태: {group.application_result}</p></div>
                  <button
                    onClick={() => handleButtonClick(group.apartment_name)}
                    style={{
                      backgroundColor: "#57b6fe",
                      color: "white",
                      border: "none",
                      padding: "8px 20px",
                      borderRadius: "5px",
                      fontSize: "0.9rem",
                      cursor: "pointer",
                    }}
                  >
                    더보기
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {isModalOpen && (
          <div className="modal" style={modalStyles.modal}>
            <div style={modalStyles.modalContent}>
              <button onClick={closeModal} style={modalStyles.closeButton}>
                &times;
              </button>
              <h2>{modalData?.apartment_name}</h2>
              <div style={{ width: "100%", overflowX: "auto", marginTop: "20px" }}>
                {/* modalData에 HTML 테이블이 포함된 경우 */}
                <div dangerouslySetInnerHTML={{ __html: modalData }} />
              </div>
            </div>
          </div>
        )}

        <button
          className="carousel-control-prev"
          type="button"
          data-bs-target="#apt_competiton"
          data-bs-slide="prev"
          style={{
            position: "absolute",
            top: "110px",
            padding: "4px 6px",
            width: "25px",
            height: "25px",
            backgroundColor: "#57b6fe",
            color: "white",
            borderRadius: "50%",
            fontSize: "10px",
          }}
        >
          <span className="carousel-control-prev-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Previous</span>
        </button>

        <button
          className="carousel-control-next"
          type="button"
          data-bs-target="#apt_competiton"
          data-bs-slide="next"
          style={{
            position: "absolute",
            top: "110px",
            padding: "4px 6px",
            width: "25px",
            height: "25px",
            backgroundColor: "#57b6fe",
            color: "white",
            borderRadius: "50%",
            fontSize: "10px",
          }}
        >
          <span className="carousel-control-next-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Next</span>
        </button>
      </div>






<div id="unranked_competiton" className="carousel slide" data-bs-ride="carousel" style={{ maxWidth: "300px" }}>
  <h4 style={{ textAlign: "center", marginBottom: "8px", fontWeight: "bold", color: "#6a75ca", fontSize: "1.2rem" }}>무순위</h4>
  <div className="carousel-inner">
    {unranked_grouped_data && unranked_grouped_data.map((group, index) => (
      <div key={index} className={`carousel-item ${index === 0 ? "active" : ""}`}>
        <div className="card" style={{ width: "14rem", margin: "auto" }}>
          <div className="card-body">
            <a
              style={{ textDecoration: "none", color: "inherit", fontSize: "1.2rem", fontWeight: "bold" }}
            >
              {group.apartment_name}
            </a>
            <br /><br />
            <div><p style={{ fontSize: "0.9rem" }}>경쟁률: {group.total_competition_rate}</p></div>
            <div><p style={{ fontSize: "0.9rem" }}>상태: {group.application_result}</p></div>
            <button
              onClick={() => handleButtonClick(group.apartment_name)}
              style={{
                backgroundColor: "#57b6fe",
                color: "white",
                border: "none",
                padding: "8px 20px",
                borderRadius: "5px",
                fontSize: "0.9rem",
                cursor: "pointer",
              }}
            >
              더보기
            </button>
          </div>
        </div>
      </div>
    ))}
  </div>
{/* 모달 */}
{isModalOpen && (
  <div className="modal" style={modalStyles.modal}>
    <div style={modalStyles.modalContent}>
      <button onClick={closeModal} style={modalStyles.closeButton}>
        &times;
      </button>
      <h2>{modalData?.apartment_name}</h2>
      <div style={{ width: "100%", overflowX: "auto", marginTop: "20px" }}>
        {/* modalData에 HTML 테이블이 포함된 경우 */}
        <div dangerouslySetInnerHTML={{ __html: modalData }} />
      </div>
    </div>
  </div>
)}
  <button
    className="carousel-control-prev"
    type="button"
    data-bs-target="#unranked_competiton"
    data-bs-slide="prev"
    style={{
      position: "absolute",
      top: "110px",
      padding: "4px 6px",
      width: "25px",
      height: "25px",
      backgroundColor: "#57b6fe",
      color: "white",
      borderRadius: "50%",
      fontSize: "10px",
    }}
  >
    <span className="carousel-control-prev-icon" aria-hidden="true"></span>
    <span className="visually-hidden">Previous</span>
  </button>
  <button
    className="carousel-control-next"
    type="button"
    data-bs-target="#unranked_competiton"
    data-bs-slide="next"
    style={{
      position: "absolute",
      top: "110px",
      padding: "4px 6px",
      width: "25px",
      height: "25px",
      backgroundColor: "#57b6fe",
      color: "white",
      borderRadius: "50%",
      fontSize: "10px",
    }}
  >
    <span className="carousel-control-next-icon" aria-hidden="true"></span>
    <span className="visually-hidden">Next</span>
  </button>
</div>
</div>
</div>
</div>
  {/* 최신 경쟁률 제목 */}
  <h3 style={{ textAlign: "left"}}>다가올 청약</h3> {/* 텍스트 왼쪽 정렬 */}
  <div className="container" style={{ maxWidth: "750px", margin: "0px", border: "2px solid #57b6fe", borderRadius: "10px", padding: "15px", backgroundColor: "#f9f9f9" }}>
    
    <div className="d-flex justify-content-around flex-wrap" style={{ gap: "15px" }}>
      <div id="apt_upcoming_applications" className="carousel slide" data-bs-ride="carousel" style={{ maxWidth: "250px" }}>
        <h4 style={{ textAlign: "center", marginBottom: "8px", fontWeight: "bold", color: "#6a75ca", fontSize: "1.2rem" }}>아파트</h4>
        <div className="carousel-inner">
        {apt_upcoming_data && apt_upcoming_data.map((group, index) => (
          <div key={index} className={`carousel-item ${index === 0 ? "active" : ""}`}>
            <div className="card" style={{ width: "14rem", margin: "auto" }}>
              <div className="card-body" style={{ padding: "10px" }}>
                <a 
                  style={{ textDecoration: "none", color: "inherit", fontSize: "1.2rem", fontWeight: "bold" }}>
                  { group.apartment_name }
                </a>
                <br /><br />
                <div><p style={{ fontSize: "0.9rem", margin: "0" }}>청약 접수 시작일 : { group.application_period_start }</p></div>
                <div><p style={{ fontSize: "0.9rem", margin: "0" }}>지역 : { group.region }</p></div>
                <button 
                  onClick={() => handleButtonClick(group.apartment_name)}
                  style={{ backgroundColor: "#57b6fe", color: "white", border: "none", padding: "8px 15px", borderRadius: "5px", fontSize: "0.9rem", cursor: "pointer", marginTop: "10px" }}>
                  더보기
                </button>
              </div>
            </div>
          </div>
        ))}
        </div>
        {isModalOpen && (
  <div className="modal" style={modalStyles.modal}>
    <div style={modalStyles.modalContent}>
      <button onClick={closeModal} style={modalStyles.closeButton}>
        &times;
      </button>
      <h2>{modalData?.apartment_name}</h2>
      <div style={{ width: "100%", overflowX: "auto", marginTop: "20px" }}>
        {/* modalData에 HTML 테이블이 포함된 경우 */}
        <div dangerouslySetInnerHTML={{ __html: modalData }} />
      </div>
    </div>
  </div>
)}
        <button className="carousel-control-prev" type="button" data-bs-target="#apt_upcoming_applications" data-bs-slide="prev" 
          style={{ position: "absolute", top: "100px", zIndex: 1, padding: "3px 5px", width: "25px", height: "25px", backgroundColor: "#57b6fe", color: "white", borderRadius: "50%", fontSize: "10px" }}>
          <span className="carousel-control-prev-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Previous</span>
        </button>
        <button className="carousel-control-next" type="button" data-bs-target="#apt_upcoming_applications" data-bs-slide="next" 
          style={{ position: "absolute", top: "100px", zIndex: 1, padding: "3px 5px", width: "25px", height: "25px", backgroundColor: "#57b6fe", color: "white", borderRadius: "50%", fontSize: "10px" }}>
          <span className="carousel-control-next-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Next</span>
        </button>
      </div>

      <div className="d-flex justify-content-around flex-wrap" style={{ gap: "15px" }}>
      <div id="unranked_upcoming_data" className="carousel slide" data-bs-ride="carousel" style={{ maxWidth: "250px" }}>
        <h4 style={{ textAlign: "center", marginBottom: "8px", fontWeight: "bold", color: "#6a75ca", fontSize: "1.2rem" }}>무순위</h4>
        <div className="carousel-inner">
        {unranked_upcoming_data && unranked_upcoming_data.map((group, index) => (
          <div key={index} className={`carousel-item ${index === 0 ? "active" : ""}`}>
            <div className="card" style={{ width: "14rem", margin: "auto" }}>
              <div className="card-body" style={{ padding: "10px" }}>
                <a
                  style={{ textDecoration: "none", color: "inherit", fontSize: "1.2rem", fontWeight: "bold" }}>
                  { group.apartment_name }
                </a>
                <br /><br />
                <div><p style={{ fontSize: "0.9rem", margin: "0" }}>청약 접수 시작일 : { group.application_period_start }</p></div>
                <div><p style={{ fontSize: "0.9rem", margin: "0" }}>지역 : { group.region }</p></div>
                <button 
                  onClick={() => handleButtonClick(group.apartment_name)}
                  style={{ backgroundColor: "#57b6fe", color: "white", border: "none", padding: "8px 15px", borderRadius: "5px", fontSize: "0.9rem", cursor: "pointer", marginTop: "10px" }}>
                  더보기
                </button>
              </div>
            </div>
          </div>
        ))}
        </div>
        {isModalOpen && (
          <div className="modal" style={modalStyles.modal}>
            <div style={modalStyles.modalContent}>
              <button onClick={closeModal} style={modalStyles.closeButton}>
                &times;
              </button>
              <h2>{modalData?.apartment_name}</h2>
              <div style={{ width: "100%", overflowX: "auto", marginTop: "20px" }}>
                {/* modalData에 HTML 테이블이 포함된 경우 */}
                <div dangerouslySetInnerHTML={{ __html: modalData }} />
              </div>
            </div>
          </div>
        )}
        <button className="carousel-control-prev" type="button" data-bs-target="#unranked_upcoming_data" data-bs-slide="prev" 
          style={{ position: "absolute", zIndex: 1, top: "100px", padding: "3px 5px", width: "25px", height: "25px", backgroundColor: "#57b6fe", color: "white", borderRadius: "50%", fontSize: "10px" }}>
          <span className="carousel-control-prev-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Previous</span>
        </button>
        <button className="carousel-control-next" type="button" data-bs-target="#unranked_upcoming_data" data-bs-slide="next" 
          style={{ position: "absolute", zIndex: 1, top: "100px", padding: "3px 5px", width: "25px", height: "25px", backgroundColor: "#57b6fe", color: "white", borderRadius: "50%", fontSize: "10px" }}>
          <span className="carousel-control-next-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Next</span>
        </button>
      </div>
    </div>
  </div>
  </div>




<div><Chatbot /></div>
  



 </div>



  );
};
const modalStyles = {
  modal: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%", // 높이를 100%로 설정하여 화면 전체를 덮도록 수정
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "10px",
    width: "80%",
    maxWidth: "1100px",
    maxHeight: "90vh", // 모달 최대 높이 설정
    overflowY: "auto", // 세로 스크롤 활성화
    position: "relative", // 닫기 버튼을 위치시키기 위한 상대적 위치
  },
  closeButton: {
    backgroundColor: "transparent",
    border: "none",
    fontSize: "1.5rem",
    position: "absolute",
    top: "10px",
    right: "10px",
    cursor: "pointer",
  },
};
export default Main;











