import React from 'react';
import {BackButton} from '@vkruglikov/react-telegram-web-app';
import {useNavigate} from 'react-router-dom';

const GetTested = () => {
    let navigate = useNavigate()
    return (
        <>
            <BackButton onClick={() => navigate(-1)}/>
            <div className="get-tested">
                <div className="get-tested__header">
                    <h1 className="get-tested__header__title">Get Tested</h1>
                    <p className="get-tested__header__text">Select a diagnostic to see their available time
                        slots.</p>
                </div>
            </div>
        </>
    );
};

export default GetTested;
