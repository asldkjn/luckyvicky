function fetchAndCreateWordCloud(selector, jsonFile) {
    fetch(jsonFile)
        .then(response => response.json())
        .then(data => {
            // JSON 데이터를 words 배열로 변환
            const words = Object.keys(data).map(word => ({
                text: word,
                size: Math.sqrt(data[word]) * 10,  // 빈도수에 따라 글자 크기 조정
                frequency: data[word]               // 빈도수 추가
            }));

            console.log("Loaded words:", words); // words 배열이 올바르게 생성되었는지 확인
            createWordCloud(selector, words);
        })
        .catch(error => console.error("Error loading JSON file:", error));
}

function createWordCloud(selector, words) {
    const width = 500, height = 400;

    // Tooltip 요소 생성
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background-color", "rgba(0, 0, 0, 0.7)")
        .style("color", "#fff")
        .style("padding", "5px")
        .style("border-radius", "5px")
        .style("font-size", "12px")
        .style("visibility", "hidden")
        .style("pointer-events", "none");

    const layout = d3.layout.cloud()
        .size([width, height])
        .words(words)  // words 배열 그대로 전달
        .padding(5)
        .rotate(0)
        .fontSize(d => d.size)
        .on("end", wordsWithMetaData => draw(wordsWithMetaData));

    layout.start();

    function draw(wordsWithMetaData) {
        console.log("Words to be drawn:", wordsWithMetaData); // draw 함수 내 words 배열 확인

        // d3에서 전달받은 words가 metaData를 가지고 있는지 확인
        const enhancedWords = wordsWithMetaData.map(d => ({
            text: d.text,
            size: d.size,
            frequency: d.frequency || d.original.frequency, // d.frequency가 없을 때 original 데이터에서 frequency 가져오기
            x: d.x,
            y: d.y,
        }));

        console.log("Enhanced Words:", enhancedWords); // 확인용

        d3.select(selector).selectAll("svg").remove();

        const svg = d3.select(selector).append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${width / 2}, ${height / 2})`);

        svg.selectAll("text")
            .data(enhancedWords)
            .enter().append("text")
            .style("font-size", d => `${d.size}px`)
            .style("fill", (_, i) => d3.schemeCategory10[i % 10])
            .attr("text-anchor", "middle")
            .attr("transform", d => `translate(${d.x}, ${d.y})`)
            .text(d => d.text)
            .on("mouseover", (event, d) => {
                tooltip.style("visibility", "visible")
                    .text(`단어: ${d.text}, 빈도수: ${d.frequency}`);
            })
            .on("mousemove", (event) => {
                tooltip.style("top", `${event.pageY + 10}px`)
                    .style("left", `${event.pageX + 10}px`);
            })
            .on("mouseout", () => {
                tooltip.style("visibility", "hidden");
            });
    }
}

// JSON 파일 경로 설정 및 워드 클라우드 생성 호출
fetchAndCreateWordCloud("#positive_b", "sorted_merged_avene_가격_positive_b_words.json");
fetchAndCreateWordCloud("#positive_i", "sorted_merged_avene_가격_positive_i_words.json");
fetchAndCreateWordCloud("#negative_b", "sorted_merged_avene_가격_negative_b_words.json");
fetchAndCreateWordCloud("#negative_i", "sorted_merged_avene_가격_negative_i_words.json");
