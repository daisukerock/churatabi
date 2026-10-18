const {chromium,webkit}=require('playwright');
const launchOptions=engine=>({headless:true,...(engine==='chromium'&&process.env.CHROME_EXECUTABLE?{executablePath:process.env.CHROME_EXECUTABLE}:{})});
module.exports={chromium,webkit,launchOptions};
