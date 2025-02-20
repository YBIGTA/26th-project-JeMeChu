import React from "react";
import { useState } from "react";
import { Tag, Input, Button } from "antd"; // npm install antd --save
import { PlusOutlined, CheckOutlined } from "@ant-design/icons";
import "./DishSelect.css";

const { CheckableTag } = Tag; // antd component 임 https://ant.design/components/overview

const DishSelect = ({ onSearch }) => {
  const [dishTags, setDishTags] = useState([]); // 선택된 태그 상태 관리
  const [preferences, setPreferences] = useState("");
  const [menu, setMenu] = useState("");

  // tag 입력창
  const tags = ["한식", "중식", "일식", "양식", "동남아"];
  const TypeDisplay = ({ data }) => {
    // tag checkable => click 시 chekced 됨 상태로 표시
    const handleChange = (tag, checked) => {
      const nextDishTags = checked
        ? [...dishTags, tag] // 체크 시 추가
        : dishTags.filter((t) => t !== tag); // 해제 시 제거

      console.log("dishTag Selected: ", nextDishTags);
      setDishTags(nextDishTags);
    };

    return (
      <div className="tag-container">
        {data.map((tag, index) => {
          const isSelected = dishTags.includes(tag); // 태그 선택 여부 확인
          return (
            <CheckableTag
              key={index}
              checked={isSelected} // checked 속성 올바르게 설정
              className={`tag ${isSelected ? "tag-selected" : ""}`}
              onChange={(checked) => handleChange(tag, checked)}
            >
              <span style={{ marginRight: "3px", fontSize: "10px" }}>
                <CheckOutlined />
              </span>
              {tag}
            </CheckableTag>
          );
        })}
      </div>
    );
  };

  // 검색 버튼 클릭 핸들러
  const handleSearch = () => {
    onSearch(dishTags, menu, preferences);
  };

  return (
    <div className="DishSelect">
      <div className="query-container">
        <div className="dishOption">Select Dish</div>
        {/* 태그 버튼 */}
        <TypeDisplay data={tags} />
        {/* 검색 입력 */}
        <Input
          placeholder="다른 거 먹고싶어요.."
          value={menu}
          onChange={(e) => setMenu(e.target.value)}
          className="custom-input"
        />
      </div>

      <div className="query-container">
        <div className="dishOption">Dining Preferences</div>
        {/* 다이닝 선호도 입력 */}
        <Input
          type="text"
          placeholder="(ex) 조용, 룸, 유아동반.."
          value={preferences}
          onChange={(e) => setPreferences(e.target.value)}
          className="custom-input"
        />
      </div>

      {/* 검색 버튼 */}
      <div className="button-container">
        <Button onClick={handleSearch} className="srch-button">
          내 맞춤 식당 찾아보기
        </Button>
      </div>
    </div>
  );
};

export default DishSelect;
