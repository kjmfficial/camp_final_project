const ProgressBar = ({ currentStep, totalSteps }) => {
    const progress = (currentStep / totalSteps) * 100;
  
    return (
      <div className="progress-container">
        <div className="progress-bar" style={{ width: `${progress}%` }}/>
        <span className="progress-text">
          {currentStep}/{totalSteps} 단계
        </span>
      </div>
    );
  };
  
  export default ProgressBar
  