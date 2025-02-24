import React from "react";

/**
 * reason 문자열 안에서 core 문자열을 찾아 색상 강조 처리
 * @param reason 전체 문장 (예: "이가네 양꼬치 양갈비의 리뷰에서 '주차도 지원되어서 좋아요'...")
 * @param core 강조하고 싶은 단어 (예: "주차")
 */
export function highlightCore(reason: string, core: string | string[]) {
  if (!reason || !core) return reason;
  // ✅ core가 문자열이면 배열로 변환 (추가된 부분)
  const coreArray = Array.isArray(core) ? core : core.split(", ").map(item => item.trim());

  // ✅ core 배열을 이용해 순차적으로 단어 강조
  let highlightedText = reason;
  coreArray.forEach((word) => {
    const regex = new RegExp(`(${word})`, "gi"); // 대소문자 구분 없이 검색
    highlightedText = highlightedText.replace(
      regex,
      `<span style="color: red; font-weight: normal;">$1</span>` // ✅ 강조 스타일 적용
    );
  });

  // ✅ `dangerouslySetInnerHTML`을 사용하여 HTML 태그 적용 (추가된 부분)
  return <span dangerouslySetInnerHTML={{ __html: highlightedText }} />;
}