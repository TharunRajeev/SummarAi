import axios from "axios";
import { API_URL } from "./config";
import { getJSON } from "./helper";

export const state = {
  videoId: "",
  detailed:false,
  summary: "",
  title: "",
  thumbnailUrl: "",
};

export const loadSummary = async function () {
  try {
    var data = null;
    if (!state.detailed) 
      data = await getJSON(`${API_URL}/summary?v=${state.videoId}`);
    else 
      data = await getJSON(`${API_URL}/summary/detailed?v=${state.videoId}`);
    state.summary = data.data;
  } catch (err) {
    throw err;
  }
};

export const loadMetaData = async function (videoId) {
  try {
    const requestUrl = `https://youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`;
    const result = await axios.get(requestUrl);
    state.title = result.data.title;
    state.thumbnailUrl = result.data.thumbnail_url;
  } catch (err) {
    throw err;
  }
};
