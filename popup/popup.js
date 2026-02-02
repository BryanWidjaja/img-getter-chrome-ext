document.getElementById("getImages").addEventListener("click", async () => {
  const imagesDiv = document.getElementById("images");
  imagesDiv.innerHTML = "";

  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tabs.length) {
    imagesDiv.textContent = "No active tab";
    return;
  }

  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      func: () => {
        const img = document.querySelector(
          'img[alt="Photo for tag placement"]',
        );

        if (!img) return null;

        return img.src;
      },
    });

    if (!results || !results.length || !results[0].result) {
      imagesDiv.textContent = "Image not found";
      return;
    }

    const src = results[0].result;

    const link = document.createElement("a");
    link.href = "#";
    link.textContent = src;
    link.style.display = "block";

    link.addEventListener("click", (e) => {
      e.preventDefault();
      chrome.tabs.create({ url: src, active: false });
    });

    imagesDiv.appendChild(link);
  } catch (err) {
    console.error(err);
    imagesDiv.textContent = "Cannot access this page";
  }
});
