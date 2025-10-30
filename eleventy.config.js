module.exports = function (eleventyConfig) {
  eleventyConfig.addWatchTarget("docs/data");

  eleventyConfig.addPassthroughCopy({
    "site/assets": "assets"
  });

  eleventyConfig.addFilter("formatNumber", (value) => {
    const number = Number(value);
    if (!Number.isFinite(number)) {
      return "0";
    }

    return new Intl.NumberFormat("es-CL").format(number);
  });

  eleventyConfig.addFilter("formatDecimal", (value, maximumFractionDigits = 1) => {
    const number = Number(value);
    if (!Number.isFinite(number)) {
      return "0";
    }

    return new Intl.NumberFormat("es-CL", {
      minimumFractionDigits: 0,
      maximumFractionDigits
    }).format(number);
  });

  return {
    dir: {
      input: "site",
      includes: "_includes",
      layouts: "_includes/layouts",
      data: "_data",
      output: "_site"
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};
