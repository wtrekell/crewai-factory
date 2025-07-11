import warnings

import yaml
warnings.filterwarnings('ignore')
from crew import DesignCrew, CodingCrew
import logging


from helpers.helper import load_env

load_env()

logging.basicConfig(
    filename="crew_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class CrewFactoryCrew:

    def run(self):
        try:
            # test_query = ["write me a sample crew.py file for the crew factory project"]
            # query_results = crew.query_knowledge(test_query)

            # if query_results:
            #     print("Query Results:", query_results)
            # else:
            #     print("No results from the knowledge base. Verify the sources.")

            logging.info("Initializing agents and tasks...")

            with open('crew_input.yaml', 'r') as file:
                crew_input = yaml.safe_load(file)

            design_crew_instance = DesignCrew(crew_input.get('crew_name'))
            design_crew = design_crew_instance.crew()
            result = design_crew.kickoff(crew_input)
            self.save_result(result, 'design_crew')

            # Show where files were created
            print(f"\n✅ Design Crew completed successfully!")
            print(f"📁 Crew files saved to: {design_crew_instance.output_dir}")
            print(f"   └── config/tasks.yaml")
            print(f"   └── config/agents.yaml") 
            print(f"   └── src/input.json")
            print(f"📄 Results summary: design_crew_results.md")
            
            return result

            # TODO: Re-enable after fixing rate limiting
            # crew_input['design_crew_result'] = result.raw if result else None
            # coding_crew = CodingCrew(crew_input.get('crew_name')).crew()
            # result = coding_crew.kickoff(crew_input)
            # self.save_result(result, 'coding_crew')
            # return result

        except Exception as e:
            logging.error(f"Unexpected error occurred: {e}")
            raise e

    @staticmethod
    def save_result(result, crew_name=None):
        try:
            output_file_path = f"{crew_name}_results.md" if crew_name else "crew_results.md"
            with open(output_file_path, "w") as file:
                file.write("# Crew Execution Results\n\n")
                file.write(str(result))
            logging.info(f"Results saved to {output_file_path}.")
        except IOError as e:
            logging.error(f"Failed to save results: {e}")
            print(f"Error: Could not save results to file. {e}")


# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
    print("## Welcome to Crew Factory!")
    print("-------------------------------")
    # var1 = input(dedent("""Enter variable 1: """))
    # var2 = input(dedent("""Enter variable 2: """))

    result = CrewFactoryCrew().run()

    print("\n\n########################")
    print("## Here is you custom crew run result:")
    print("########################\n")
    print(result)
