import ProfCard from "./ProfCard";
import NavBar from "../../components/NavBar";
import Footers from "../../components/footers";
import AcademicCard from "./AkademicCard";

function AkademicPage() {
	return (
		<>
			<NavBar></NavBar>
			<ProfCard></ProfCard>
			<AcademicCard></AcademicCard>
            <Footers></Footers>
		</>
	);
}

export default AkademicPage;
