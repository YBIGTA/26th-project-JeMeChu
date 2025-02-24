import React from "react";

/**
 * reason 문자열 안에서 core 문자열을 찾아 색상 강조 처리
 * @param reason 전체 문장 (예: "이가네 양꼬치 양갈비의 리뷰에서 '주차도 지원되어서 좋아요'...")
 * @param core 강조하고 싶은 단어 (예: "주차")
 */
export function highlightCore(reason: string, core: string) {
  if (!reason || !core) return reason;

  // core를 기준으로 문자열 split
  const parts = reason.split(core);

  // core 단어가 문장에 없다면 그대로 반환
  if (parts.length === 1) {
    return reason;
  }

  // core 부분만 강조해서 다시 합침
  return (
    <>
      {parts.map((part, idx) => (
        <React.Fragment key={idx}>
          {part}
          {idx < parts.length - 1 && (
            <span style={{ color: "red", fontWeight: "bold" }}>
              {core}
            </span>
          )}
        </React.Fragment>
      ))}
    </>
  );
}