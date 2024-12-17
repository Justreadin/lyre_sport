// Placeholder content for live scores
const scores = [
    { match: "Team A vs Team B", score: "2-1" },
    { match: "Team C vs Team D", score: "1-3" },
    { match: "Team E vs Team F", score: "0-0" }
];

// Placeholder content for news articles
const news = [
    { title: "Big Win for Team A!", content: "Team A secured a big win over Team B." },
    { title: "Player X Breaks Record", content: "Player X set a new record today." },
    { title: "Upcoming Match Preview", content: "Exciting match coming up!" }
];

document.addEventListener("DOMContentLoaded", () => {
    // Populate Live Scores
    const scoreContainer = document.getElementById('score-container');
    scores.forEach(item => {
        const div = document.createElement('div');
        div.className = 'score';
        div.innerHTML = `<strong>${item.match}</strong>: ${item.score}`;
        scoreContainer.appendChild(div);
    });

    // Populate News
    const newsContainer = document.getElementById('news-container');
    news.forEach(item => {
        const article = document.createElement('article');
        article.className = 'news-item';
        article.innerHTML = `<h3>${item.title}</h3><p>${item.content}</p>`;
        newsContainer.appendChild(article);
    });

    // Add comment to post
    const submitCommentButton = document.getElementById('submit-comment');
    if (submitCommentButton) {
        submitCommentButton.addEventListener('click', async () => {
            const commentBox = document.getElementById('comment-box');
            const comment = commentBox.value.trim();
            const postId = document.getElementById("post-id").value;
            
            if (comment) {
                try {
                    // Send comment to the server
                    const response = await fetch(`/post/${postId}/add_comment`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ content: comment })
                    });

                    if (response.ok) {
                        // Add comment to UI
                        const commentsContainer = document.getElementById('comments-container');
                        const newComment = document.createElement('div');
                        newComment.className = 'user-comment';
                        newComment.innerHTML = `<strong>You:</strong> ${comment}`;
                        commentsContainer.appendChild(newComment);
                        commentBox.value = ''; // Clear the comment box
                    } else {
                        alert("Failed to add comment. Please try again.");
                    }
                } catch (error) {
                    console.error("Error adding comment:", error);
                    alert("An error occurred. Please try again.");
                }
            } else {
                alert("Please enter a comment.");
            }
        });
    }

    // Refresh comments from the server
    const refreshCommentsButton = document.getElementById("refresh-comments");
    if (refreshCommentsButton) {
        refreshCommentsButton.addEventListener("click", () => {
            const postId = document.getElementById("post-id").value;
            fetchComments(postId);
        });
    }

    // Fetch comments function
    async function fetchComments(postId) {
        try {
            const response = await fetch(`/post/${postId}/comments`);
            if (!response.ok) throw new Error("Failed to fetch comments.");

            const comments = await response.json();

            // Clear existing comments
            const commentsSection = document.getElementById("comments-section");
            commentsSection.innerHTML = "";

            comments.forEach(comment => {
                const commentEl = document.createElement("div");
                commentEl.classList.add("comment");
                commentEl.innerHTML = `<p><strong>${comment.username}</strong>: ${comment.content}</p>
                                       <small>${comment.timestamp}</small>`;
                commentsSection.appendChild(commentEl);
            });
        } catch (error) {
            console.error("Error fetching comments:", error);
            alert("An error occurred while fetching comments.");
        }
    }



        const carousel = document.querySelector("#testimonial-carousel");
        const slides = carousel.querySelector(".testimonial-slides");
        const prevButton = document.querySelector("#prev-slide");
        const nextButton = document.querySelector("#next-slide");
        const indicators = document.querySelector(".carousel-indicators");
      
        let currentSlideIndex = 0;
      
        const updateCarousel = () => {
          const totalSlides = slides.children.length;
          slides.style.transition = "transform 0.5s ease-in-out";
          slides.style.transform = `translateX(-${currentSlideIndex * 100}%)`;
      
          // Update active indicator
          const activeIndicator = indicators.querySelector(".active");
          if (activeIndicator) activeIndicator.classList.remove("active");
          indicators.children[currentSlideIndex].classList.add("active");
      
          // Loop back to the beginning/end if out of bounds
          if (currentSlideIndex < 0) {
            currentSlideIndex = totalSlides - 1;
            slides.style.transition = "none";  // Skip transition when looping back
            slides.style.transform = `translateX(-${currentSlideIndex * 100}%)`;
          } else if (currentSlideIndex >= totalSlides) {
            currentSlideIndex = 0;
            slides.style.transition = "none";  // Skip transition when looping back
            slides.style.transform = `translateX(-${currentSlideIndex * 100}%)`;
          }
        };
      
        const createIndicators = () => {
          const totalSlides = slides.children.length;
          indicators.innerHTML = ""; // Clear existing indicators
          for (let i = 0; i < totalSlides; i++) {
            const indicator = document.createElement("li");
            indicator.classList.add("indicator");
            indicator.addEventListener("click", () => {
              currentSlideIndex = i;
              updateCarousel();
            });
            indicators.appendChild(indicator);
          }
          updateCarousel();
        };
      
        prevButton.addEventListener("click", () => {
          currentSlideIndex--;
          updateCarousel();
        });
      
        nextButton.addEventListener("click", () => {
          currentSlideIndex++;
          updateCarousel();
        });
      
        // Auto-slide functionality (optional)
        const autoSlideInterval = setInterval(() => {
          currentSlideIndex++;
          updateCarousel();
        }, 5000); // Change slides every 5 seconds
      
        // Pause auto-sliding when hovering
        carousel.addEventListener("mouseenter", () => clearInterval(autoSlideInterval));
        carousel.addEventListener("mouseleave", () => setInterval(autoSlideInterval, 5000));
      
        createIndicators();
      });
      


