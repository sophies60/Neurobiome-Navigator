import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

class SurveyType(Enum):
    ORAL_HEALTH = "oral_health"
    IMPULSE_CONTROL = "impulse_control"

class SurveyManager:
    """Manages survey data collection and storage in session state."""
    
    def __init__(self):
        # Initialize session state for all survey modules
        if 'survey_data' not in st.session_state:
            st.session_state.survey_data = {
                SurveyType.ORAL_HEALTH.value: {
                    'responses': {},
                    'last_updated': None
                },
                SurveyType.IMPULSE_CONTROL.value: {
                    'responses': {},
                    'last_updated': None
                }
            }
    
    def update_responses(self, survey_type: SurveyType, responses: Dict[str, int]) -> None:
        """Update survey responses for a specific survey type."""
        if survey_type.value not in st.session_state.survey_data:
            st.session_state.survey_data[survey_type.value] = {
                'responses': {},
                'last_updated': None
            }
        
        st.session_state.survey_data[survey_type.value]['responses'] = responses
        st.session_state.survey_data[survey_type.value]['last_updated'] = datetime.now().isoformat()
    
    def get_responses(self, survey_type: SurveyType) -> Dict[str, int]:
        """Get responses for a specific survey type."""
        return st.session_state.survey_data.get(survey_type.value, {}).get('responses', {})
    
    def get_oral_health_summary(self) -> str:
        """Generate a summary of oral health responses."""
        responses = self.get_responses(SurveyType.ORAL_HEALTH)
        if not responses:
            return "No oral health data available. Please complete the oral health survey."
        
        issues = []
        
        if responses.get('Bleeding Gums', 0) >= 3:
            issues.append("bleeding gums")
        if responses.get('Dry Mouth', 0) >= 3:
            issues.append("dry mouth")
        if responses.get('Bad Breath', 0) >= 3:
            issues.append("bad breath")
        if responses.get('Tooth Sensitivity', 0) >= 3:
            issues.append("tooth sensitivity")
        if responses.get('Mouth Pain', 0) >= 3:
            issues.append("mouth pain")
        
        if not issues:
            return "Your oral health appears to be in good condition."
        else:
            return f"Consider addressing these oral health concerns: {', '.join(issues)}."
    
    def get_impulse_control_summary(self) -> str:
        """Generate a summary of impulse control responses."""
        responses = self.get_responses(SurveyType.IMPULSE_CONTROL)
        if not responses:
            return "No impulse control data available. Please complete the impulse control survey."
        
        concerns = []
        
        if responses.get('Gambling', 0) >= 3:
            concerns.append("gambling urges")
        if responses.get('Shopping', 0) >= 3:
            concerns.append("impulsive shopping")
        if responses.get('Eating', 0) >= 3:
            concerns.append("binge eating")
        if responses.get('Hypersexuality', 0) >= 3:
            concerns.append("increased sexual urges")
        if responses.get('Punding', 0) >= 3:
            concerns.append("repetitive, purposeless activities")
        
        if not concerns:
            return "Your impulse control appears to be well managed."
        else:
            return f"Consider discussing these impulse control concerns with your healthcare provider: {', '.join(concerns)}."
    
    def get_last_updated(self, survey_type: SurveyType) -> Optional[str]:
        """Get when a specific survey was last updated."""
        if 'survey_data' not in st.session_state:
            return None
        return st.session_state.survey_data.get(survey_type.value, {}).get('last_updated')
    
    def get_last_updated_any(self) -> Optional[str]:
        """Get when any survey was last updated."""
        latest = None
        for survey_type in SurveyType:
            updated = self.get_last_updated(survey_type)
            if updated and (latest is None or updated > latest):
                latest = updated
        return latest

def show_survey() -> None:
    """Display the survey form and handle submissions."""
    st.subheader("Personal Health Survey")
    
    with st.form("health_survey"):
        st.markdown("### Diet & Nutrition")
        diet_quality = st.slider(
            "How would you rate your diet quality?", 
            1, 10, 5,
            help="1 = Poor, 10 = Excellent"
        )
        
        st.markdown("### Oral Health")
        brush_frequency = st.select_slider(
            "How often do you brush your teeth?",
            options=["Less than once a day", "Once a day", "Twice a day", "After every meal"]
        )
        
        st.markdown("### Lifestyle")
        sleep_quality = st.slider(
            "How would you rate your sleep quality?",
            1, 10, 5,
            help="1 = Poor, 10 = Excellent"
        )
        
        stress_level = st.slider(
            "How would you rate your stress level?",
            1, 10, 5,
            help="1 = No stress, 10 = Extremely stressed"
        )
        
        # Submit button
        submitted = st.form_submit_button("Update My Snapshot")
        if submitted:
            survey = SurveyManager()
            survey.update_response("diet_quality", diet_quality)
            survey.update_response("brush_frequency", brush_frequency)
            survey.update_response("sleep_quality", sleep_quality)
            survey.update_response("stress_level", stress_level)
            st.success("Your responses have been saved!")

def get_survey_summary() -> str:
    """Generate a summary of survey responses with personalized insights."""
    if 'survey_responses' not in st.session_state or not st.session_state.survey_responses:
        return "Complete the health survey to see your personalized insights."
    
    responses = st.session_state.survey_responses
    summary_parts = []
    
    # Diet summary
    if 'diet_quality' in responses:
        diet_score = responses['diet_quality']['value']
        if diet_score >= 8:
            summary_parts.append("Excellent diet quality!")
        elif diet_score >= 5:
            summary_parts.append("Good diet quality with room for improvement.")
        else:
            summary_parts.append("Consider improving your diet for better health.")
    
    # Oral health summary
    if 'brush_frequency' in responses:
        brush_freq = responses['brush_frequency']['value']
        if brush_freq in ["Twice a day", "After every meal"]:
            summary_parts.append("Great oral care routine!")
        else:
            summary_parts.append("Consider brushing more frequently for better oral health.")
    
    # Lifestyle summary
    if 'sleep_quality' in responses and 'stress_level' in responses:
        sleep = responses['sleep_quality']['value']
        stress = responses['stress_level']['value']
        
        if sleep <= 4 and stress >= 7:
            summary_parts.append("Focus on improving sleep and managing stress.")
        elif sleep <= 4:
            summary_parts.append("Consider improving your sleep quality.")
        elif stress >= 7:
            summary_parts.append("Try stress management techniques like meditation.")
    
    return " ".join(summary_parts) if summary_parts else "Complete the survey to see your personalized insights."
