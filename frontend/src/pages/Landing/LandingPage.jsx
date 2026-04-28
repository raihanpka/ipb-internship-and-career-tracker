import JobCards from "./JobCards";
import CompanyCards from "./CompanyCards";
import HeroSec from "./HeroSec.jsx"
import NavBar from "../../components/NavBar"
import Footers from "../../components/footers.jsx";

function LandingPage() {
	return (
		<>
			<NavBar></NavBar>
			<HeroSec></HeroSec>
			<CompanyCards></CompanyCards>
			<JobCards></JobCards>
			<Footers></Footers>
		</>
	);
}



export default LandingPage;
